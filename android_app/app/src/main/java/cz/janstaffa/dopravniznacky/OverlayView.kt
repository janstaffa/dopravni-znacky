/*
 * Copyright 2022 The TensorFlow Authors. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package cz.janstaffa.dopravniznacky

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Rect
import android.graphics.RectF
import android.util.AttributeSet
import android.util.Log
import android.view.View
import androidx.core.content.ContextCompat
import java.util.LinkedList
import kotlin.math.max
import org.tensorflow.lite.task.gms.vision.detector.Detection
import kotlin.math.roundToInt

class OverlayView(context: Context?, attrs: AttributeSet?) : View(context, attrs) {

    private var results: List<Detection> = LinkedList<Detection>()
    private var boxPaint = Paint()
    private var textBackgroundPaint = Paint()
    private var textPaint = Paint()

    private var scaleFactor: Float = 1f

    private var bounds = Rect()


    var showBoxes = true
    var showLabels = false
    var showScores = true

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


    init {
        initPaints()
    }

    fun clear() {
        textPaint.reset()
        textBackgroundPaint.reset()
        boxPaint.reset()
        invalidate()
        initPaints()
    }

    private fun initPaints() {
        textBackgroundPaint.color = Color.BLACK
        textBackgroundPaint.style = Paint.Style.FILL
        textBackgroundPaint.textSize = 50f

        textPaint.color = Color.WHITE
        textPaint.style = Paint.Style.FILL
        textPaint.textSize = 50f

        boxPaint.color = ContextCompat.getColor(context!!, R.color.bounding_box_color)
        boxPaint.strokeWidth = 5F
        boxPaint.style = Paint.Style.STROKE
    }

    override fun draw(canvas: Canvas) {
        super.draw(canvas)
        Log.d("OverlayView", "Drawing")

        for (result in results) {
            val boundingBox = result.boundingBox

            val top = boundingBox.top * scaleFactor
            val bottom = boundingBox.bottom * scaleFactor
            val left = boundingBox.left * scaleFactor
            val right = boundingBox.right * scaleFactor


            // Draw bounding box around detected objects
            if (showBoxes) {
                val drawableRect = RectF(left, top, right, bottom)
                canvas.drawRect(drawableRect, boxPaint)
            }

            // Create text to display alongside detected objects
            var detailText = ""
            if (showLabels) {
                val classId = result.categories[0].label.trim().toInt()
                //println("Len: ${label.length}, Val: ${label.toString().toByteArray().contentToString()}, New Len: ${label.toString().trim().length}")
                detailText = labels[classId]
                if (showScores) detailText += ", "
            }
            if (showScores)
                detailText += (result.categories[0].score * 100).roundToInt().toString() + "%"
            //  detailText += String.format("%.2f", result.categories[0].score)

            if (detailText.isNotEmpty()) {
                // Draw rect behind display text
                textBackgroundPaint.getTextBounds(detailText, 0, detailText.length, bounds)
                val textWidth = bounds.width()
                val textHeight = bounds.height()
                canvas.drawRect(
                    left,
                    top - textHeight - boxPaint.strokeWidth - 2 * BOUNDING_RECT_TEXT_PADDING,
                    left + textWidth + 2 * BOUNDING_RECT_TEXT_PADDING,
                    top - boxPaint.strokeWidth,
                    textBackgroundPaint
                )

                // Draw text for detected object
                canvas.drawText(
                    detailText,
                    left + BOUNDING_RECT_TEXT_PADDING,
                    top - boxPaint.strokeWidth - BOUNDING_RECT_TEXT_PADDING,
                    textPaint
                )
            }

        }
    }

    fun setResults(
        detectionResults: MutableList<Detection>,
        imageHeight: Int,
        imageWidth: Int,
    ) {
        results = detectionResults

        // PreviewView is in FILL_START mode. So we need to scale up the bounding box to match with
        // the size that the captured images will be displayed.
        scaleFactor = max(width * 1f / imageWidth, height * 1f / imageHeight)
    }

    companion object {
        private const val BOUNDING_RECT_TEXT_PADDING = 8
    }
}
