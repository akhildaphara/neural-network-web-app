#!/usr/bin/env python
# coding: utf-8

# # Import Libraries

# In[ ]:


#get_ipython().run_line_magic('matplotlib', 'inline')

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt


# # Download Data

# In[ ]:


(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()


# # Plot Examples

# In[ ]:


plt.figure(figsize=(10, 10))

for i in range(16):
    plt.subplot(4, 4, i + 1)
    plt.imshow(x_train[i], cmap='binary')
    plt.xlabel(str(y_train[i]))
    plt.xticks([])
    plt.yticks([])
plt.show()


# # Normalize Data

# In[ ]:


x_train = np.reshape(x_train, (60000, 784))
x_train = x_train / 255.

x_test = np.reshape(x_test, (10000, 784))
x_test = x_test / 255.


# # Create a Neural Network Model

# In[ ]:


model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(32, activation='sigmoid', input_shape=(784,)),
    tf.keras.layers.Dense(32, activation='sigmoid'),
    tf.keras.layers.Dense(10, activation='softmax')
])

model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])


# # Train the Model

# In[ ]:


_ = model.fit(
    x_train, y_train,
    validation_data=(x_test, y_test),
    epochs=20, batch_size=1024,
    verbose=2
)


# # Save the Model

# In[ ]:


model.save('model.h5')


# # The ML Server

# In[ ]:


get_ipython().run_cell_magic('writefile', 'ml_server.py', "\nimport json\nimport tensorflow as tf\nimport numpy as np\nimport os\nimport random\nimport string\n\nfrom flask import Flask, request\n\napp = Flask(__name__)\n\nmodel = tf.keras.models.load_model('model.h5')\nfeature_model = tf.keras.models.Model(model.inputs, [layer.output for layer in model.layers])\n\n_, (x_test, _) = tf.keras.datasets.mnist.load_data()\nx_test = x_test / 255.\n\ndef get_prediction():\n    index = np.random.choice(x_test.shape[0])\n    image = x_test[index,:,:]\n    image_arr = np.reshape(image, (1, 784))\n    return feature_model.predict(image_arr), image\n\n@app.route('/', methods=['GET', 'POST'])\ndef index():\n    if request.method == 'POST':\n        preds, image = get_prediction()\n        final_preds = [p.tolist() for p in preds]\n        return json.dumps({'prediction': final_preds, 'image': image.tolist()})\n    return 'Welcome to the ml server'\n\nif __name__ == '__main__':\n    app.run()")


# # Streamlit Web App

# In[ ]:


get_ipython().run_cell_magic('writefile', 'app.py', "\nimport requests\nimport json\nimport numpy as np\nimport streamlit as st\nimport os\nimport matplotlib.pyplot as plt\n\nURI = 'http://127.0.0.1:5000'\n\nst.title('Neural Network Visualizer')\nst.sidebar.markdown('# Input Image')\n\nif st.button('Get random predictions'):\n    response = requests.post(URI, data={})\n    response = json.loads(response.text)\n    preds = response.get('prediction')\n    image = response.get('image')\n    image = np.reshape(image, (28, 28))\n\n    st.sidebar.image(image, width=150)\n\n    for layer, p in enumerate(preds):\n        numbers = np.squeeze(np.array(p))\n\n        plt.figure(figsize=(32, 4))\n\n        if layer == 2:\n            row = 1\n            col = 10\n        else:\n            row = 2\n            col = 16\n\n        for i, number in enumerate(numbers):\n            plt.subplot(row, col, i + 1)\n            plt.imshow((number * np.ones((8, 8, 3))).astype('float32'), cmap='binary')\n            plt.xticks([])\n            plt.yticks([])\n            if layer == 2:\n                plt.xlabel(str(i), fontsize=40)\n        plt.subplots_adjust(wspace=0.05, hspace=0.05)\n        plt.tight_layout()\n\n        st.text('Layer {}'.format(layer + 1), )\n        st.pyplot()")

