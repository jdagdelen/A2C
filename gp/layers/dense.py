from gp.layers.utils import *
from gp.layers.pooling import max_pool_2d

import tensorflow as tf


def dense_p(name, x, w=None, output_dim=16, initializer=tf.contrib.layers.xavier_initializer(), l2_strength=0.0,
            bias=0.0):
    """
    Fully connected layer
    :param name: (string) The name scope provided by the upper tf.name_scope('name') as scope.
    :param x: (tf.tensor) The input to the layer (N, D).
    :param w: (tf.tensor) Variable representing the pretrained weights
    :param output_dim: (integer) It specifies H, the output second dimension of the fully connected layer [ie:(N, H)]
    :param initializer: (tf.contrib initializer) The initialization scheme, He et al. normal or Xavier normal are recommended.
    :param l2_strength:(weight decay) (float) L2 regularization parameter.
    :param bias: (float) Amount of bias.
    :return out: The output of the layer. (N, H)
    """
    n_in = x.get_shape()[-1].value
    with tf.variable_scope(name):
        if not w:
            w = variable_with_weight_decay([n_in, output_dim], initializer, l2_strength)
        b = tf.get_variable("layer_biases", [output_dim], tf.float32, tf.constant_initializer(bias))
        output = tf.nn.bias_add(tf.matmul(x, w), b)
        return output


def dense(name, x, w=None, output_dim=16, initializer=tf.contrib.layers.xavier_initializer(), l2_strength=0.0,
          bias=0.0,
          activation=None, batchnorm_enabled=False, max_pool_enabled=True, dropout_keep_prob=1.0,
          is_training=True
          ):
    """
    This block is responsible for a fully connected followed by optional (non-linearity, dropout, max-pooling).
    Note that: "is_training" should be passed by a correct value based on being in either training or testing.
    :param name: (string) The name scope provided by the upper tf.name_scope('name') as scope.
    :param x: (tf.tensor) The input to the layer (N, D).
    :param w: (tf.tensor) Variable representing the pretrained weights
    :param output_dim: (integer) It specifies H, the output second dimension of the fully connected layer [ie:(N, H)]
    :param initializer: (tf.contrib initializer) The initialization scheme, He et al. normal or Xavier normal are recommended.
    :param l2_strength:(weight decay) (float) L2 regularization parameter.
    :param bias: (float) Amount of bias.
    :param activation: (tf.graph operator) The activation function applied after the convolution operation. If None, linear is applied.
    :param batchnorm_enabled: (boolean) for enabling batch normalization.
    :param max_pool_enabled:  (boolean) for enabling max-pooling 2x2 to decrease width and height by a factor of 2.
    :param dropout_keep_prob: (float) for the probability of keeping neurons.
    :param is_training: (boolean) to diff. between training and testing (important for batch normalization and dropout) 
    :return out: The output of the layer. (N, H)
    """
    with tf.name_scope(name) as scope:
        dense_o_b = dense_p(name=scope, x=x, w=w, output_dim=output_dim, initializer=initializer,
                            l2_strength=l2_strength,
                            bias=bias)

        if batchnorm_enabled:
            dense_o_bn = tf.layers.batch_normalization(dense_o_b, training=is_training)
            if not activation:
                dense_a = dense_o_bn
            else:
                dense_a = activation(dense_o_bn)
        else:
            if not activation:
                dense_a = dense_o_b
            else:
                dense_a = activation(dense_o_b)

        dense_o_dr = tf.nn.dropout(dense_a, dropout_keep_prob)

        dense_o = dense_o_dr
        if max_pool_enabled:
            dense_o = max_pool_2d(scope, dense_o_dr)

    return dense_o