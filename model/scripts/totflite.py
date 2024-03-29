import shutil
import tensorflow as tf
from tflite_support import metadata
import os
import argparse
from tensorflow.lite.python.interpreter import Interpreter
import random
import glob
from tflite_support import flatbuffers
from tflite_support import metadata as _metadata
from tflite_support import metadata_schema_py_generated as _metadata_fb


QUANT_IMG_COUNT = 300
_INPUT_NORM_MEAN = 127.5
_INPUT_NORM_STD = 127.5

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model", help="Path to saved model")
parser.add_argument("-o", "--output", help="Path to write output tflite model to")
parser.add_argument("-l", "--labels", help="Path to label .txt file")
parser.add_argument("-q", "--quantize", help="Quantize the model?", action="store_true")
parser.add_argument(
    "-repd",
    "--representative_data",
    help="Path to representative images used for quantization (in PNG format)",
)
parser.add_argument(
    "-v", "--view", help="Log output metadata to console", action="store_true"
)

args = parser.parse_args()

if (
    args.model == None
    or args.output == None
    or args.labels == None
    or (args.quantize == True and args.representative_data == None)
):
    print("Missing parameters \n")
    parser.print_help()
    exit(1)

print("\n EXPORTING MODEL...\n")
# Export plain Tflite model
converter = tf.lite.TFLiteConverter.from_saved_model(args.model)
# converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

tflite_model_out_path = os.path.join(args.output, "model.tflite")

with open(tflite_model_out_path, "wb") as f:
    f.write(tflite_model)

# Add metadata and quantize
interpreter = Interpreter(model_path=tflite_model_out_path)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]["shape"][1]
width = input_details[0]["shape"][2]
#                   (file_path, is_quantized)
files_to_process = [(tflite_model_out_path, False)]

if args.quantize == True:
    print("\n QUANTIZING MODEL...\n")
    quant_image_list = glob.glob(args.representative_data + "/*.png")

    def representative_data_gen():
        dataset_list = quant_image_list
        for i in range(QUANT_IMG_COUNT):
            pick_me = random.choice(dataset_list)
            image = tf.io.read_file(pick_me)

            image = tf.io.decode_png(image, channels=3)

            image = tf.image.resize(image, [width, height])
            image = tf.cast(image / 255.0, tf.float32)
            image = tf.expand_dims(image, 0)
            yield [image]

    converter = tf.lite.TFLiteConverter.from_saved_model(args.model)

    # This enables quantization
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = representative_data_gen

    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS,
        tf.lite.OpsSet.TFLITE_BUILTINS_INT8,
    ]
    converter.target_spec.supported_types = [tf.int8]

    converter.inference_input_type = tf.uint8
    converter.inference_output_type = tf.float32

    tflite_model = converter.convert()

    quant_file_out_path = os.path.join(args.output, "model_quant.tflite")
    with open(quant_file_out_path, "wb") as f:
        f.write(tflite_model)

    files_to_process.append((quant_file_out_path, True))


print("\n ADDING METADATA...\n")
for f, is_quantized in files_to_process:
    # Creates model info.
    model_meta = _metadata_fb.ModelMetadataT()
    model_meta.name = "DZ model V2" + "(quantized)" if is_quantized else ""
    model_meta.description = (
        "Detects czech traffic signs in images. "
        "Base model - MobilenetV2 with images resized to native input shape. "
        "More: https://github.com/janstaffa/dopravni-znacky"
    )
    model_meta.version = "v2"
    model_meta.author = "Jan Staffa " "https://janstaffa.cz"
    model_meta.license = (
        "Apache License. Version 2.0 " "http://www.apache.org/licenses/LICENSE-2.0."
    )

    # Creates input info.
    input_meta = _metadata_fb.TensorMetadataT()
    input_meta.name = "image"
    input_meta.description = (
        "Input image to be classified. The expected image has shape {0}x{1}.".format(
            width, height
        )
    )
    input_meta.content = _metadata_fb.ContentT()
    input_meta.content.contentProperties = _metadata_fb.ImagePropertiesT()
    input_meta.content.contentProperties.colorSpace = _metadata_fb.ColorSpaceType.RGB
    input_meta.content.contentPropertiesType = (
        _metadata_fb.ContentProperties.ImageProperties
    )
    input_normalization = _metadata_fb.ProcessUnitT()
    input_normalization.optionsType = (
        _metadata_fb.ProcessUnitOptions.NormalizationOptions
    )
    input_normalization.options = _metadata_fb.NormalizationOptionsT()
    input_normalization.options.mean = [_INPUT_NORM_MEAN]
    input_normalization.options.std = [_INPUT_NORM_STD]
    input_meta.processUnits = [input_normalization]
    input_stats = _metadata_fb.StatsT()
    input_stats.max = [1.0]
    input_stats.min = [-1.0]
    input_meta.stats = input_stats

    # Creates output info.
    output_location_meta = _metadata_fb.TensorMetadataT()
    output_location_meta.name = "location"
    output_location_meta.description = (
        "The locations of the detected boxes. (xmin, ymin, xmax, ymax)"
    )
    output_location_meta.content = _metadata_fb.ContentT()
    output_location_meta.content.contentPropertiesType = (
        _metadata_fb.ContentProperties.BoundingBoxProperties
    )
    output_location_meta.content.contentProperties = (
        _metadata_fb.BoundingBoxPropertiesT()
    )
    output_location_meta.content.contentProperties.index = [1, 0, 3, 2]
    output_location_meta.content.contentProperties.type = (
        _metadata_fb.BoundingBoxType.BOUNDARIES
    )
    output_location_meta.content.contentProperties.coordinateType = (
        _metadata_fb.CoordinateType.RATIO
    )
    output_location_meta.content.range = _metadata_fb.ValueRangeT()
    output_location_meta.content.range.min = 2
    output_location_meta.content.range.max = 2
    output_location_meta.stats = _metadata_fb.StatsT()

    output_class_meta = _metadata_fb.TensorMetadataT()
    output_class_meta.name = "category"
    output_class_meta.description = "The classes of the detected boxes."
    output_class_meta.content = _metadata_fb.ContentT()
    output_class_meta.content.contentPropertiesType = (
        _metadata_fb.ContentProperties.FeatureProperties
    )
    output_class_meta.content.contentProperties = _metadata_fb.FeaturePropertiesT()
    output_class_meta.content.range = _metadata_fb.ValueRangeT()
    output_class_meta.content.range.min = 2
    output_class_meta.content.range.max = 2
    label_file = _metadata_fb.AssociatedFileT()
    label_file.name = os.path.basename(args.labels)
    label_file.description = "Labels of objects that this model can recognize."
    label_file.type = _metadata_fb.AssociatedFileType.TENSOR_VALUE_LABELS
    output_class_meta.associatedFiles = [label_file]
    output_class_meta.stats = _metadata_fb.StatsT()

    output_score_meta = _metadata_fb.TensorMetadataT()
    output_score_meta.name = "score"
    output_score_meta.description = "The scores of the detected boxes."
    output_score_meta.content = _metadata_fb.ContentT()
    output_score_meta.content.contentPropertiesType = (
        _metadata_fb.ContentProperties.FeatureProperties
    )
    output_score_meta.content.contentProperties = _metadata_fb.FeaturePropertiesT()
    output_score_meta.content.range = _metadata_fb.ValueRangeT()
    output_score_meta.content.range.min = 2
    output_score_meta.content.range.max = 2
    output_score_meta.stats = _metadata_fb.StatsT()

    output_number_meta = _metadata_fb.TensorMetadataT()
    output_number_meta.name = "number of detections"
    output_number_meta.description = "The number of the detected boxes."
    output_number_meta.content = _metadata_fb.ContentT()
    output_number_meta.content.contentPropertiesType = (
        _metadata_fb.ContentProperties.FeatureProperties
    )
    output_number_meta.content.contentProperties = _metadata_fb.FeaturePropertiesT()
    output_number_meta.stats = _metadata_fb.StatsT()

    # Creates subgraph info.
    group = _metadata_fb.TensorGroupT()
    group.name = "detection_result"
    group.tensorNames = [
        output_location_meta.name,
        output_class_meta.name,
        output_score_meta.name,
    ]
    subgraph = _metadata_fb.SubGraphMetadataT()
    subgraph.inputTensorMetadata = [input_meta]
    subgraph.outputTensorMetadata = [
        output_score_meta,
        output_location_meta,
        output_number_meta,
        output_class_meta,
    ]
    subgraph.outputTensorGroups = [group]
    model_meta.subgraphMetadata = [subgraph]

    b = flatbuffers.Builder(0)
    b.Finish(model_meta.Pack(b), _metadata.MetadataPopulator.METADATA_FILE_IDENTIFIER)
    metadata_buf = b.Output()

    populator = _metadata.MetadataPopulator.with_model_file(f)
    populator.load_metadata_buffer(metadata_buf)
    populator.load_associated_files([args.labels])
    populator.populate()

    if args.view:
        print(f"\nShowing metadata for: {f}")
        displayer = _metadata.MetadataDisplayer.with_model_file(f)
        print(displayer.get_metadata_json())

print("\n DONE")