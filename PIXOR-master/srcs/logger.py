# Code referenced from https://gist.github.com/gyglim/1f8dfb1b5c82627ae3efcfbbadb9f514
import tensorflow as tf
import numpy as np
import scipy.misc

"""
INFO line 15:22: tf.summary.FileWriter requires manual check. The TF 1.x summary API cannot be automatically migrated to TF 2.0, so symbols have been converted to tf.compat.v1.summary.* and must be migrated manually. Typical usage will only require changes to the summary writing logic, not to individual calls like scalar(). For examples of the new summary API, see the Effective TF 2.0 migration document or check the TF 2.0 TensorBoard tutorials.
INFO line 15:22: Renamed 'tf.summary.FileWriter' to 'tf.compat.v1.summary.FileWriter'
INFO line 19:18: Renamed 'tf.Summary' to 'tf.compat.v1.Summary'
INFO line 19:36: Renamed 'tf.Summary' to 'tf.compat.v1.Summary'
WARNING line 32:12: *.save requires manual check. (This warning is only applicable if the code saves a tf.Keras model) Keras model.save now saves to the Tensorflow SavedModel format by default, instead of HDF5. To continue saving to HDF5, add the argument save_format='h5' to the save() function.
INFO line 35:22: Renamed 'tf.Summary' to 'tf.compat.v1.Summary'
INFO line 39:33: Renamed 'tf.Summary' to 'tf.compat.v1.Summary'
INFO line 42:18: Renamed 'tf.Summary' to 'tf.compat.v1.Summary'
INFO line 52:15: Renamed 'tf.HistogramProto' to 'tf.compat.v1.HistogramProto'
INFO line 69:18: Renamed 'tf.Summary' to 'tf.compat.v1.Summary'
INFO line 69:36: Renamed 'tf.Summary' to 'tf.compat.v1.Summary'
TensorFlow 2.0 Upgrade Script
"""

try:
    from StringIO import StringIO  # Python 2.7
except ImportError:
    from io import BytesIO  # Python 3.x


class Logger(object):
    def __init__(self, log_dir):
        """Create a summary writer logging to log_dir."""
        self.writer = tf.compat.v1.summary.FileWriter(log_dir)

    def scalar_summary(self, tag, value, step):
        """Log a scalar variable."""
        summary = tf.compat.v1.Summary(value=[tf.compat.v1.Summary.Value(tag=tag, simple_value=value)])
        self.writer.add_summary(summary, step)

    def image_summary(self, tag, images, step):
        """Log a list of images."""

        img_summaries = []
        for i, img in enumerate(images):
            # Write the image to a string
            try:
                s = StringIO()
            except:
                s = BytesIO()
            scipy.misc.toimage(img).save(s, format="png")

            # Create an Image object
            img_sum = tf.compat.v1.Summary.Image(encoded_image_string=s.getvalue(),
                                       height=img.shape[0],
                                       width=img.shape[1])
            # Create a Summary value
            img_summaries.append(tf.compat.v1.Summary.Value(tag='%s/%d' % (tag, i), image=img_sum))

        # Create and write Summary
        summary = tf.compat.v1.Summary(value=img_summaries)
        self.writer.add_summary(summary, step)

    def histo_summary(self, tag, values, step, bins=1000):
        """Log a histogram of the tensor of values."""

        # Create a histogram using numpy
        counts, bin_edges = np.histogram(values, bins=bins)

        # Fill the fields of the histogram proto
        hist = tf.compat.v1.HistogramProto()
        hist.min = float(np.min(values))
        hist.max = float(np.max(values))
        hist.num = int(np.prod(values.shape))
        hist.sum = float(np.sum(values))
        hist.sum_squares = float(np.sum(values ** 2))

        # Drop the start of the first bin
        bin_edges = bin_edges[1:]

        # Add bin edges and counts
        for edge in bin_edges:
            hist.bucket_limit.append(edge)
        for c in counts:
            hist.bucket.append(c)

        # Create and write Summary
        summary = tf.compat.v1.Summary(value=[tf.compat.v1.Summary.Value(tag=tag, histo=hist)])
        self.writer.add_summary(summary, step)
        self.writer.flush()