package cz.janstaffa.dopravniznacky.fragments


import android.annotation.SuppressLint
import android.content.res.Configuration
import android.graphics.Bitmap
import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.util.Log
import android.util.Size
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.AdapterView
import android.widget.ImageView
import android.widget.Toast
import androidx.camera.core.Camera
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageAnalysis.OUTPUT_IMAGE_FORMAT_RGBA_8888
import androidx.camera.core.ImageProxy
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.content.ContextCompat
import androidx.core.view.setPadding
import androidx.fragment.app.Fragment
import androidx.navigation.Navigation
import cz.janstaffa.dopravniznacky.ObjectDetectorHelper
import cz.janstaffa.dopravniznacky.R
import cz.janstaffa.dopravniznacky.databinding.FragmentDetectorBinding
import org.tensorflow.lite.task.gms.vision.detector.Detection
import java.time.LocalDateTime
import java.util.Calendar
import java.util.LinkedList
import java.util.Locale
import java.util.Timer
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

data class DetectedSign(val signId: Int, var timeout: Long)

class DetectorFragment : Fragment(), ObjectDetectorHelper.DetectorListener {

    private val TAG = "CameraFragment"
    private val DEFAULT_TIMEOUT = 5000L

    private var _fragmentCameraBinding: FragmentDetectorBinding? = null

    private val fragmentCameraBinding
        get() = _fragmentCameraBinding!!

    private lateinit var objectDetectorHelper: ObjectDetectorHelper
    private lateinit var bitmapBuffer: Bitmap
    private var preview: Preview? = null
    private var imageAnalyzer: ImageAnalysis? = null
    private var camera: Camera? = null
    private var cameraProvider: ProcessCameraProvider? = null

    /** Blocking camera operations are performed using this executor */
    private lateinit var cameraExecutor: ExecutorService


    private lateinit var textToSpeech: TextToSpeech

    private var detectedSigns = ArrayList<DetectedSign>()

    private var lastFrameTime: Long = 0L

    private var ttsEnabled = false
    private var signTimeout = DEFAULT_TIMEOUT

    private val labels = arrayOf(
        "",
        "zákaz vjezdu",
        "zákaz vjezdu (jeden směr)",
        "zákaz předjíždění",
        "zákaz vjezdu motorových vozidel",
        "zákaz odbočení vpravo",
        "zákaz odbočení vlevo",
        "zákaz stání",
        "zákaz zastavení",
        "přikázaný směr rovně",
        "přikázaný směr vpravo",
        "přikázaný směr vlevo",
        "kruhový objezd",
        "přechod pro chodce",
        "hlavní silnice",
        "křižovatka s vedlejší komunikací",
        "stůj, dej přednost",
        "dej přednost v jízdě",
        "omezení rychlosti - 30",
        "omezení rychlosti - 50",
        "omezení rychlosti - 70",
    )

    override fun onResume() {
        super.onResume()
        // Make sure that all permissions are still present, since the
        // user could have removed them while the app was in paused state.
        if (!Permissions.hasPermissions(requireContext())) {
            Navigation.findNavController(requireActivity(), R.id.fragment_container)
                .navigate(DetectorFragmentDirections.actionCameraToPermissions())
        }
    }

    override fun onDestroyView() {
        _fragmentCameraBinding = null
        super.onDestroyView()

        // Shut down our background executor
        cameraExecutor.shutdown()
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _fragmentCameraBinding = FragmentDetectorBinding.inflate(inflater, container, false)
        return fragmentCameraBinding.root
    }

    @SuppressLint("MissingPermission")
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        objectDetectorHelper = ObjectDetectorHelper(
            context = requireContext(),
            objectDetectorListener = this
        )

        fragmentCameraBinding.openOptionsButton.setOnClickListener {
            fragmentCameraBinding.optionsLayoutWrap.optionsLayout.visibility = View.VISIBLE
        }


        textToSpeech = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                Log.d("TextToSpeech", "Initialization Success")
                textToSpeech.language = Locale.ENGLISH
            } else {
                Log.d("TextToSpeech", "Initialization Failed")
            }
        }


        // Attach listeners to UI control widgets
        initOptionsControls()
    }

    private fun initOptionsControls() {
        fragmentCameraBinding.optionsLayoutWrap.closeOptionsButton.setOnClickListener {
            fragmentCameraBinding.optionsLayoutWrap.optionsLayout.visibility = View.INVISIBLE
        }

        fragmentCameraBinding.optionsLayoutWrap.showLabelsCheckbox.setOnCheckedChangeListener { _, isChecked ->
            fragmentCameraBinding.overlay.showLabels = isChecked
        }
        fragmentCameraBinding.optionsLayoutWrap.showScoresCheckbox.setOnCheckedChangeListener { _, isChecked ->
            fragmentCameraBinding.overlay.showScores = isChecked
        }
        fragmentCameraBinding.optionsLayoutWrap.showBoxesCheckbox.setOnCheckedChangeListener { _, isChecked ->
            fragmentCameraBinding.overlay.showBoxes = isChecked
        }

        fragmentCameraBinding.optionsLayoutWrap.ttsEnabled.setOnCheckedChangeListener { _, isChecked ->
            ttsEnabled = isChecked
        }

        fragmentCameraBinding.optionsLayoutWrap.timeoutMinus.setOnClickListener {
            if (signTimeout > 0) {
                signTimeout -= 1000L
                updateControlsUi()
            }
        }

        fragmentCameraBinding.optionsLayoutWrap.timeoutPlus.setOnClickListener {
            if (signTimeout < 60000) {
                signTimeout += 1000L
                updateControlsUi()
            }
        }


        // When clicked, lower detection score threshold floor
        fragmentCameraBinding.optionsLayoutWrap.thresholdMinus.setOnClickListener {
            if (objectDetectorHelper.threshold >= 0.1) {
                objectDetectorHelper.threshold -= 0.1f
                updateControlsUi()
            }
        }

        // When clicked, raise detection score threshold floor
        fragmentCameraBinding.optionsLayoutWrap.thresholdPlus.setOnClickListener {
            if (objectDetectorHelper.threshold <= 0.8) {
                objectDetectorHelper.threshold += 0.1f
                updateControlsUi()
            }
        }

        // When clicked, reduce the number of objects that can be detected at a time
        fragmentCameraBinding.optionsLayoutWrap.maxResultsMinus.setOnClickListener {
            if (objectDetectorHelper.maxResults > 1) {
                objectDetectorHelper.maxResults--
                updateControlsUi()
            }
        }

        // When clicked, increase the number of objects that can be detected at a time
        fragmentCameraBinding.optionsLayoutWrap.maxResultsPlus.setOnClickListener {
            if (objectDetectorHelper.maxResults < 5) {
                objectDetectorHelper.maxResults++
                updateControlsUi()
            }
        }

        // When clicked, decrease the number of threads used for detection
        fragmentCameraBinding.optionsLayoutWrap.threadsMinus.setOnClickListener {
            if (objectDetectorHelper.numThreads > 1) {
                objectDetectorHelper.numThreads--
                updateControlsUi()
            }
        }

        // When clicked, increase the number of threads used for detection
        fragmentCameraBinding.optionsLayoutWrap.threadsPlus.setOnClickListener {
            if (objectDetectorHelper.numThreads < 10) {
                objectDetectorHelper.numThreads++
                updateControlsUi()
            }
        }

        // When clicked, change the underlying hardware used for inference. Current options are CPU
        // GPU, and NNAPI
        fragmentCameraBinding.optionsLayoutWrap.spinnerDelegate.setSelection(0, false)
        fragmentCameraBinding.optionsLayoutWrap.spinnerDelegate.onItemSelectedListener =
            object : AdapterView.OnItemSelectedListener {
                override fun onItemSelected(p0: AdapterView<*>?, p1: View?, p2: Int, p3: Long) {
                    objectDetectorHelper.currentDelegate = p2
                    updateControlsUi()
                }

                override fun onNothingSelected(p0: AdapterView<*>?) {
                    /* no op */
                }
            }

        // When clicked, change the underlying model used for object detection
        fragmentCameraBinding.optionsLayoutWrap.spinnerModel.setSelection(0, false)
        fragmentCameraBinding.optionsLayoutWrap.spinnerModel.onItemSelectedListener =
            object : AdapterView.OnItemSelectedListener {
                override fun onItemSelected(p0: AdapterView<*>?, p1: View?, p2: Int, p3: Long) {
                    objectDetectorHelper.currentModel = p2
                    updateControlsUi()
                }

                override fun onNothingSelected(p0: AdapterView<*>?) {
                    /* no op */
                }
            }
    }

    // Update the values displayed in the bottom sheet. Reset detector.
    private fun updateControlsUi() {
        fragmentCameraBinding.optionsLayoutWrap.maxResultsValue.text =
            objectDetectorHelper.maxResults.toString()
        fragmentCameraBinding.optionsLayoutWrap.thresholdValue.text =
            String.format("%.2f", objectDetectorHelper.threshold)
        fragmentCameraBinding.optionsLayoutWrap.threadsValue.text =
            objectDetectorHelper.numThreads.toString()

        val signTimeoutVal = "${(signTimeout / 1000).toInt()}s"
        fragmentCameraBinding.optionsLayoutWrap.timeoutValue.text = signTimeoutVal

        // Needs to be cleared instead of reinitialized because the GPU
        // delegate needs to be initialized on the thread using it when applicable
        objectDetectorHelper.clearObjectDetector()
        fragmentCameraBinding.overlay.clear()
    }

    // Initialize CameraX, and prepare to bind the camera use cases
    private fun setUpCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(requireContext())
        cameraProviderFuture.addListener(
            {
                // CameraProvider
                cameraProvider = cameraProviderFuture.get()

                // Build and bind the camera use cases
                bindCameraUseCases()
            },
            ContextCompat.getMainExecutor(requireContext())
        )
    }

    // Declare and bind preview, capture and analysis use cases
    @SuppressLint("UnsafeOptInUsageError")
    private fun bindCameraUseCases() {

        // CameraProvider
        val cameraProvider =
            cameraProvider ?: throw IllegalStateException("Camera initialization failed.")

        // CameraSelector - makes assumption that we're only using the back camera
        val cameraSelector =
            CameraSelector.Builder().requireLensFacing(CameraSelector.LENS_FACING_BACK).build()

        // Preview. Only using the 4:3 ratio because this is the closest to our models
        preview =
            Preview.Builder()
                .setTargetResolution(Size(640, 480))
                .build()

        // ImageAnalysis. Using RGBA 8888 to match how our models work
        imageAnalyzer =
            ImageAnalysis.Builder()
                .setTargetResolution(Size(640, 480))
                .setTargetRotation(fragmentCameraBinding.viewFinder.display.rotation)
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .setOutputImageFormat(OUTPUT_IMAGE_FORMAT_RGBA_8888)
                .build()
                // The analyzer can then be assigned to the instance
                .also {
                    it.setAnalyzer(cameraExecutor) { image ->
                        if (!::bitmapBuffer.isInitialized) {
                            // The image rotation and RGB image buffer are initialized only once
                            // the analyzer has started running
                            bitmapBuffer = Bitmap.createBitmap(
                                image.width,
                                image.height,
                                Bitmap.Config.ARGB_8888
                            )
                        }

                        detectObjects(image)
                    }
                }

        // Must unbind the use-cases before rebinding them
        cameraProvider.unbindAll()

        try {
            // A variable number of use-cases can be passed here -
            // camera provides access to CameraControl & CameraInfo
            camera = cameraProvider.bindToLifecycle(this, cameraSelector, preview, imageAnalyzer)

            // Attach the viewfinder's surface provider to preview use case
            preview?.setSurfaceProvider(fragmentCameraBinding.viewFinder.surfaceProvider)
        } catch (exc: Exception) {
            Log.e(TAG, "Use case binding failed", exc)
        }
    }

    private fun detectObjects(image: ImageProxy) {
        // Copy out RGB bits to the shared bitmap buffer
        image.use { bitmapBuffer.copyPixelsFromBuffer(image.planes[0].buffer) }

        val imageRotation = image.imageInfo.rotationDegrees
        // Pass Bitmap and rotation to the object detector helper for processing and detection
        objectDetectorHelper.detect(bitmapBuffer, imageRotation)
    }

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        imageAnalyzer?.targetRotation = fragmentCameraBinding.viewFinder.display.rotation
    }


    // Update UI after objects have been detected. Extracts original image height/width
    // to scale and place bounding boxes properly through OverlayView
    override fun onResults(
        results: MutableList<Detection>?,
        inferenceTime: Long,
        imageHeight: Int,
        imageWidth: Int
    ) {
        val calendar = Calendar.getInstance()

        if (lastFrameTime == 0L) {
            lastFrameTime = calendar.timeInMillis
        } else {
            val now = calendar.timeInMillis
            val timeDelta = now - lastFrameTime

            // Log.d(TAG, "TIME DELTA $timeDelta")

            val newDetectedSigns = ArrayList<DetectedSign>()

            for (i in detectedSigns.indices) {
                detectedSigns[i].timeout -= timeDelta
                if (detectedSigns[i].timeout > 0)
                    newDetectedSigns.add(detectedSigns[i])
            }

            detectedSigns = newDetectedSigns
            lastFrameTime = now
        }

        activity?.runOnUiThread {
            fragmentCameraBinding.optionsLayoutWrap.inferenceTimeVal.text =
                String.format("%d ms", inferenceTime)


            val fps = 1000.0 / inferenceTime
            fragmentCameraBinding.fpsDisplay.text = String.format("FPS: %.2f", fps)
            fragmentCameraBinding.inferenceTimeDisplay.text =
                String.format("Inference time: %d ms", inferenceTime)

            fragmentCameraBinding.signDetailDisplay.removeAllViews()

            results?.let {
                for (res in it) {
                    val classId = res.categories[0].label.trim().toInt()
                    var signExists = detectedSigns.any { x ->
                        x.signId == classId
                    }

                    if (!signExists) {
                        if (ttsEnabled && !textToSpeech.isSpeaking) {
                            textToSpeech.speak(
                                this.labels[classId],
                                TextToSpeech.QUEUE_FLUSH,
                                null,
                                ""
                            )
                        }
                        detectedSigns.add(DetectedSign(classId, signTimeout))
                    }
                }

                if (detectedSigns.size > 0)
                    fragmentCameraBinding.noSignsDetectedText.visibility = View.INVISIBLE
                else
                    fragmentCameraBinding.noSignsDetectedText.visibility = View.VISIBLE


                for (sign in detectedSigns) {
                    val uri = "@drawable/z_%d".format(sign.signId)

                    val imgResource =
                        resources.getIdentifier(uri, "drawable", context?.packageName ?: "")

                    val signImage = ImageView(context)
                    signImage.setImageResource(imgResource)
                    signImage.setPadding(5)
                    fragmentCameraBinding.signDetailDisplay.addView(signImage)
                }
            }
            // Pass necessary information to OverlayView for drawing on the canvas
            fragmentCameraBinding.overlay.setResults(
                results ?: LinkedList<Detection>(),
                imageHeight,
                imageWidth
            )

            // Force a redraw
            fragmentCameraBinding.overlay.invalidate()
        }
    }

    override fun onError(error: String) {
        activity?.runOnUiThread {
            Toast.makeText(requireContext(), error, Toast.LENGTH_SHORT).show()
        }
    }

    override fun onInitialized() {
        objectDetectorHelper.setupObjectDetector()
        // Initialize our background executor
        cameraExecutor = Executors.newSingleThreadExecutor()

        // Wait for the views to be properly laid out
        fragmentCameraBinding.viewFinder.post {
            // Set up the camera and its use cases
            setUpCamera()
        }

        /*val layoutParams = fragmentCameraBinding.displayWrap.layoutParams
        layoutParams.width = 100
        fragmentCameraBinding.displayWrap.layoutParams = layoutParams
        */
        fragmentCameraBinding.progressCircular.visibility = View.GONE
    }
}
