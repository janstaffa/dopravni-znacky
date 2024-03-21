package cz.janstaffa.dopravniznacky

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.*
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.util.Size
import android.widget.ImageView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageProxy
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.content.ContextCompat
import cz.janstaffa.dopravniznacky.databinding.ActivityMainBinding
import cz.janstaffa.dopravniznacky.ml.DzModel
import cz.janstaffa.dopravniznacky.ml.DzModel2
import cz.janstaffa.dopravniznacky.ml.DzModel4Meta
import org.tensorflow.lite.DataType
import org.tensorflow.lite.support.common.FileUtil
import org.tensorflow.lite.support.image.ImageProcessor
import org.tensorflow.lite.support.image.TensorImage
import org.tensorflow.lite.support.image.ops.ResizeOp
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import kotlin.system.exitProcess


class MainActivity : AppCompatActivity() {
    private lateinit var viewBinding: ActivityMainBinding

    private var imageCapture: ImageCapture? = null

    private lateinit var cameraExecutor: ExecutorService


    private lateinit var viewOverlay: ImageView
    private val paint = Paint()

    private lateinit var model: DzModel4Meta


    private lateinit var imageProcessor: ImageProcessor

    private lateinit var labels:List<String>

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewBinding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(viewBinding.root)
        viewOverlay = findViewById(R.id.viewOverlay)

        // Request camera permissions
        if (allPermissionsGranted()) {
            startCamera()
        } else {
            requestPermissions()
        }

        model = DzModel4Meta.newInstance(this)


        imageProcessor = ImageProcessor.Builder().add(ResizeOp(480, 640, ResizeOp.ResizeMethod.BILINEAR)).build()

        labels = FileUtil.loadLabels(this, "labels.txt")

        cameraExecutor = Executors.newSingleThreadExecutor()
    }


    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)

        cameraProviderFuture.addListener({
            // Used to bind the lifecycle of cameras to the lifecycle owner
            val cameraProvider: ProcessCameraProvider = cameraProviderFuture.get()

            // Preview
            val preview = Preview.Builder().setTargetResolution(IMAGE_RESOLUTION)
                .build()
                .also {
                    it.setSurfaceProvider(viewBinding.viewFinder.surfaceProvider)
                }

            imageCapture = ImageCapture.Builder().setTargetResolution(IMAGE_RESOLUTION)
                .build()

            val imageAnalyzer =
                ImageAnalysis.Builder()
                    .setTargetResolution(IMAGE_RESOLUTION)
                    .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                    .setOutputImageFormat(ImageAnalysis.OUTPUT_IMAGE_FORMAT_RGBA_8888)
                    .build()
                    .also {
                        it.setAnalyzer(cameraExecutor) { image ->
                            detectObjects(image)
                        }
                    }


            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA

            try {
                // Unbind use cases before rebinding
                cameraProvider.unbindAll()

                // Bind use cases to camera
                cameraProvider.bindToLifecycle(
                    this, cameraSelector, preview, imageCapture, imageAnalyzer)


            } catch(exc: Exception) {
                Log.e(TAG, "Use case binding failed", exc)
            }

        }, ContextCompat.getMainExecutor(this))
    }

    private fun detectObjects(image: ImageProxy) {
        val mutable = Bitmap.createBitmap(viewOverlay.width, viewOverlay.height, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(mutable)

        val bitmap = image.toBitmap()
        image.close()
        //val ti = TensorImage.fromBitmap(bitmap)
        //inputFeature0.loadArray()
        // Runs model inference and gets result.
        val tensorImage = TensorImage(DataType.FLOAT32)
        tensorImage.load(bitmap)
        //tensorImage = imageProcessor.process(tensorImage)

        // Runs model inference and gets result
        //println("size: ${tensorImage.tensorBuffer.flatSize}")
        val outputs = model.process(tensorImage.tensorBuffer)
        /*val outputs = model.process(tensorImage)

        println("outputs: ${outputs.outputAsTensorBuffer}")*/
        val scores = outputs.numberOfDetectionsAsTensorBuffer.floatArray
        //val classes = outputs.outputFeature3AsTensorBuffer.floatArray
        //val boxes = outputs.outputFeature1AsTensorBuffer.floatArray

        println("scores ${scores.contentToString()}")
        //println("classes ${classes.contentToString()}")
        //println("boxes ${boxes.size}")




        //val locations = outputs.locationsAsTensorBuffer.floatArray
        //val classes = outputs.classesAsTensorBuffer.floatArray
        //val scores = outputs.scoresAsTensorBuffer.floatArray

        /*val h = mutable.height
        val w = mutable.width
        paint.textSize = h/15f
        paint.strokeWidth = h/85f
        var x = 0

        //println("labels ${labels.size}")
        scores.forEachIndexed { index, fl ->
            if(!classes[index].rem(1).equals(0.0f)) {
                return
            }

            x = index
            x *= 4
            if(fl > 0.3){
                paint.color = Color.WHITE
                paint.style = Paint.Style.STROKE
                canvas.drawRect(RectF(boxes[x+1] * w, boxes[x] * h, boxes[x+3] * w, boxes[x+2] * h), paint)
                paint.style = Paint.Style.FILL
                canvas.drawText(classes[index].toString() +" "+fl.toString(), boxes[x+1] * w, boxes[x] * h - 10f, paint)
            }
        }

        runOnUiThread {
            viewOverlay.setImageBitmap(mutable)
        }*/

    }

    private fun requestPermissions() {
        activityResultLauncher.launch(REQUIRED_PERMISSIONS)
    }


    private fun allPermissionsGranted() = REQUIRED_PERMISSIONS.all {
        ContextCompat.checkSelfPermission(
            baseContext, it) == PackageManager.PERMISSION_GRANTED
    }

    override fun onDestroy() {
        super.onDestroy()
        cameraExecutor.shutdown()
        model.close()
    }

    companion object {
        private const val TAG = "DopravniZnackyApp"
        private val REQUIRED_PERMISSIONS =
            mutableListOf (Manifest.permission.CAMERA).apply {
                if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.P) {
                    add(Manifest.permission.WRITE_EXTERNAL_STORAGE)
                }
            }.toTypedArray()
        private val IMAGE_RESOLUTION = Size(640, 480)

    }

    private val activityResultLauncher =
        registerForActivityResult(
            ActivityResultContracts.RequestMultiplePermissions())
        { permissions ->
            // Handle Permission granted/rejected
            var permissionGranted = true
            permissions.entries.forEach {
                if (it.key in REQUIRED_PERMISSIONS && !it.value)
                    permissionGranted = false
            }
            if (!permissionGranted) {
                Toast.makeText(baseContext,
                    "Permission request denied",
                    Toast.LENGTH_SHORT).show()
                exitProcess(0)
            } else {
                startCamera()
            }
        }

}


