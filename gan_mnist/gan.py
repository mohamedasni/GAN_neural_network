import tensorflow as tf
import numpy as np
import datetime
import matplotlib.pyplot as plt

# Lets load our mnist data
from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("MNIST_data/")

'''
Note: For clarity purposes a certain notation consistancy was implemented.
d_ : stands for discriminator specific variables
g_ : stands for generator specific variables
'''

# Lets define our discriminator model
def discriminator(images, reuse=False):
    # This will allow us to call the model more than once have it reuse variables
    if (reuse):
        tf.get_variable_scope().reuse_variables()


    # First convolutional layers
    # This finds 32 different 5 x 5 pixel features
    # Lets create our weight variable
    d_w1 = tf.get_variable('d_w1', [5, 5, 1, 32], initializer=tf.truncated_normal_initializer(stddev=0.02))
    # Lets create our bias variable
    d_b1 = tf.get_variable('d_b1', [32], initializer=tf.constant_initializer(0))
    # Apply Tensorflow's standard convolution function
    d1 = tf.nn.conv2d(input=images, filter=d_w1, strides=[1, 1, 1, 1], padding='SAME')
    # Add our bias
    d1 = d1 + d_b1
    # Apply Relu activation function
    d1 = tf.nn.relu(d1)
    d1 = tf.nn.avg_pool(d1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

    # Second convolutional layers
    # This fidns 64 different 5 x 5 pixel features
    # Lets create our weight variable
    d_w2 = tf.get_variable('d_w2', [5, 5, 32, 64], initializer=tf.truncated_normal_initializer(stddev=0.02))
    # Lets create our bias variable
    d_b2 = tf.get_variable('d_b2', [64], initializer=tf.constant_initializer(0))
    # Apply Tensorflow's standard convolution function
    d2 = tf.nn.conv2d(input=d1, filter=d_w2, strides=[1, 1, 1, 1], padding='SAME')
    # Add our bias
    d2 = d2 + d_b2
    # Apply Relu activation function
    d2 = tf.nn.relu(d2)
    d2 = tf.nn.avg_pool(d2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

    # First fully connected layer
    # Lets create our weight variable
    d_w3 = tf.get_variable('d_w3', [7 * 7 * 64, 1024], initializer=tf.truncated_normal_initializer(stddev=0.02))
    # Lets create our bias variable
    d_b3 = tf.get_variable('d_b3', [1024], initializer=tf.constant_initializer(0))
    # Reshape our data/tensor
    d3 = tf.reshape(d2, [-1, 7 * 7 * 64])
    # Multiply values by the weights and add bias
    d3 = tf.matmul(d3, d_w3) + d_b3
    # Apply Relu activation function
    d3 = tf.nn.relu(d3)

    # Second fully connected layer
    # Lets create our weight variable
    d_w4 = tf.get_variable('d_w4', [1024, 1], initializer=tf.truncated_normal_initializer(stddev=0.02))
    # Lets create our bias variable
    d_b4 = tf.get_variable('d_b4', [1], initializer=tf.constant_initializer(0))
    # Multiply by weights and add bias
    d4 = tf.matmul(d3, d_w4) + d_b4

    return d4

# Lets define our generator model
def generator(z, batch_size, z_dim, reuse=False):
    # Once more this will allow us to call the model more than once and have it resuse variables
    if (reuse):
        tf.get_variable_scope().reuse_variables()

    # Lets create our weight variable
    g_w1 = tf.get_variable('g_w1', [z_dim, 3136], dtype=tf.float32, initializer=tf.truncated_normal_initializer(stddev=0.02))
    # Lets create our bias variable
    g_b1 = tf.get_variable('g_b1', [3136], initializer=tf.truncated_normal_initializer(stddev=0.02))
    # Multiply and add bias
    g1 = tf.matmul(z, g_w1) + g_b1
    # Reshape our data
    g1 = tf.reshape(g1, [-1, 56, 56, 1])
    g1 = tf.contrib.layers.batch_norm(g1, epsilon=1e-5, scope='bn1')
    # Apply Relu activation function
    g1 = tf.nn.relu(g1)

    # Lets create our weight variable
    g_w2 = tf.get_variable('g_w2', [3, 3, 1, z_dim/2], dtype=tf.float32, initializer=tf.truncated_normal_initializer(stddev=0.02))
    # Lets create our bias variable
    g_b2 = tf.get_variable('g_b2', [z_dim/2], initializer=tf.truncated_normal_initializer(stddev=0.02))
    # Apply Tensorflow's standard convolution function
    g2 = tf.nn.conv2d(g1, g_w2, strides=[1, 2, 2, 1], padding='SAME')
    g2 = g2 + g_b2
    g2 = tf.contrib.layers.batch_norm(g2, epsilon=1e-5, scope='bn2')
    # Apply Relu activation function
    g2 = tf.nn.relu(g2)
    g2 = tf.image.resize_images(g2, [56, 56])

    # Lets create our weight variable
    g_w3 = tf.get_variable('g_w3', [3, 3, z_dim/2, z_dim/4], dtype=tf.float32, initializer=tf.truncated_normal_initializer(stddev=0.02))
    # Lets create our bias variable
    g_b3 = tf.get_variable('g_b3', [z_dim/4], initializer=tf.truncated_normal_initializer(stddev=0.02))
    # Apply Tensorflow's standard convolution function
    g3 = tf.nn.conv2d(g2, g_w3, strides=[1, 2, 2, 1], padding='SAME')
    g3 = g3 + g_b3
    g3 = tf.contrib.layers.batch_norm(g3, epsilon=1e-5, scope='bn3')
    g3 = tf.nn.relu(g3)
    g3 = tf.image.resize_images(g3, [56, 56])

    # Final convolution with one output channel
    # Lets create our weight variable
    g_w4 = tf.get_variable('g_w4', [1, 1, z_dim/4, 1], dtype=tf.float32, initializer=tf.truncated_normal_initializer(stddev=0.02))
    # Lets create our bias variable
    g_b4 = tf.get_variable('g_b4', [1], initializer=tf.truncated_normal_initializer(stddev=0.02))
    g4 = tf.nn.conv2d(g3, g_w4, strides=[1, 2, 2, 1], padding='SAME')
    g4 = g4 + g_b4
    # Apply sigmoid activation function
    g4 = tf.sigmoid(g4)

    return g4

# reset tensorflow's default graph and lets start training this thing!
tf.reset_default_graph()
batch_size =100
z_dimension = 100

z_placeholder = tf.placeholder(tf.float32,[None,z_dimension],name='z_placeholder')
x_placeholder = tf.placeholder(tf.float32,[None,28,28,1],name='x_placeholder')

# Create a child scope in order to allow us to call the discriminator twice
with tf.variable_scope(tf.get_variable_scope()):
    Gz = generator(z_placeholder, batch_size, z_dimension)
    # Gz holds the generated images

    Dx = discriminator(x_placeholder)
    # Dx will hold discriminator prediction probabilities
    # for the real MNIST images

    Dg = discriminator(Gz, reuse=True)

# Get our loss for real and fake discriminator and generator
d_loss_real = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.ones_like(Dx),logits=Dx))
d_loss_fake = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.zeros_like(Dg),logits=Dg))
g_loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.ones_like(Dg),logits=Dg))

tvars = tf.trainable_variables()
d_vars = [var for var in tvars if 'd_' in var.name]
g_vars = [var for var in tvars if 'g_' in var.name]

print ([v.name for v in d_vars])
print ([v.name for v in g_vars])

# Apply adam optimization based on the loss we got previously
with tf.variable_scope(tf.get_variable_scope()):
    # Train the discriminator
    d_trainer_fake = tf.train.AdamOptimizer(0.0003).minimize(d_loss_fake, var_list=d_vars)
    d_trainer_real = tf.train.AdamOptimizer(0.0003).minimize(d_loss_real, var_list=d_vars)

    # Train the generator
    g_trainer = tf.train.AdamOptimizer(0.0001).minimize(g_loss, var_list=g_vars)

# Define graphs that we will generate for Tensorboard
tf.summary.scalar('Discriminator_loss_real',d_loss_real)
tf.summary.scalar('Discriminator_loss_fake',d_loss_fake)
tf.summary.scalar('Generator_loss',g_loss)

# Lets start our session!
sess = tf.Session()
sess.run(tf.global_variables_initializer())

# Tensorboard stuff
with tf.variable_scope(tf.get_variable_scope()) as scope:
    images_for_tensorboard = generator(z_placeholder, batch_size, z_dimension,reuse=True)
    tf.summary.image('Generated_images', images_for_tensorboard, 5)
    merged = tf.summary.merge_all()
    logdir = 'Tensorboard/' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '/'
    writer = tf.summary.FileWriter(logdir,sess.graph)

#Pre-train discriminator for 3000 iterations - this allows for better training overall
for i in range(3000):
    z_batch = np.random.normal(0, 1, size=[batch_size,z_dimension])
    real_image_batch = mnist.train.next_batch(batch_size)[0].reshape([batch_size,28,28,1])
    _,__,dLossReal,dLossFake = sess.run([d_trainer_real,d_trainer_fake,d_loss_real,d_loss_fake],
                                       feed_dict={x_placeholder:real_image_batch,z_placeholder:z_batch})
    # Print our loss for real and fake after every 100 iterations
    if(i%100==0):
        print ('dLossReal: ',dLossReal,'dLossFake: ',dLossFake)

#Train discriminator and generator together for 100,000 iterations - This part will take a while, so maybe go grab a coffee?
for i in range(100000):
    real_image_batch = mnist.train.next_batch(batch_size)[0].reshape([batch_size,28,28,1])
    z_batch = np.random.normal(0,1,size=[batch_size,z_dimension])

    _,__,dLossReal,dLossFake = sess.run([d_trainer_real,d_trainer_fake,d_loss_real,d_loss_fake],
                                        feed_dict={x_placeholder:real_image_batch,z_placeholder:z_batch})
    z_batch = np.random.normal(0,1,size=[batch_size,z_dimension])
    _ = sess.run(g_trainer,feed_dict={z_placeholder:z_batch})

    if i%10 ==0:
        z_batch = np.random.normal(0,1,size=[batch_size,z_dimension])
        summary = sess.run(merged,feed_dict={x_placeholder:real_image_batch,z_placeholder:z_batch})
        writer.add_summary(summary,i)

    if i%100==0:
        print ('Iteration:',i,'at',datetime.datetime.now())
        z_batch = np.random.normal(0,1,size=[batch_size,z_dimension])
        generated_image = generator(z_placeholder,1,z_dimension, reuse=True)
        images = sess.run(generated_image,feed_dict={z_placeholder:z_batch})
        # plt.imshow(images[0].reshape([28,28]),cmap='Greys')
        # plt.savefig('Generated_images/'+str(i)+'.jpg')

        img = images[0].reshape([1,28,28,1])
        result = discriminator(x_placeholder)
        estimate = sess.run(result,feed_dict={x_placeholder:img})
        print ('Estimate:',estimate)
