import numpy as np

class OneHiddenLayerNN:
    """
    @brief: One hidden layer neural network with batch gradient descent.
            Currently supporting only relu, tanh and sigmoid activation functions.
    """
    def __init__(self, number_of_neurons, batch_size = 20, hidden_activation='relu',
                       out_activation='sigmoid', epochs=100, learning_rate=0.1):
        """
        :param number_of_neurons: number of neurons in hidden layer.
        :param batch_size: batch size.
        :param hidden_activation: hidden layer activation function.
        :param out_activation: out layer activation function.
        :param epochs: how many times do gradient descent.
        :param learning_rate: learning rate.
        """
        self.nn_size = number_of_neurons
        self.epochs = epochs
        self.alpha = learning_rate
        self.W_h = None
        self.W_out = None
        self.batch_size = batch_size
        self.hidden_func = hidden_activation
        self.out_func = out_activation

    @staticmethod
    def __activation(z, func_name):
        """
        :param z: dot(X, W_h).
        :param func_name: function name to compute.
        :return: activation_function(z).
        """
        if func_name == 'relu':
            # relu = max(0, z).
            return np.maximum(z, 0)
        elif func_name == 'tanh':
            # tanh = (e^z - e(-z)) / (e^z + e(-z)).
            return np.tanh(z)
        elif func_name == 'sigmoid':
            # sigmoid = 1 / (1 + e^(-z)).
            return 1 / (1 + np.exp(-z))

    @staticmethod
    def __d_activation(func_out, func_name):
        """
        :param func_out: dot(prev_layer, W_current).
        :param func_name: function name to compute.
        :return: derivative of activation function.
        """
        if func_name == 'relu':
            # d(relu) = 1 if relu > 0 else 0.
            func_o_tmp = func_out.copy()
            func_o_tmp[func_out <= 0] = 0
            func_o_tmp[func_out > 0] = 1
            return func_o_tmp
        elif func_name == 'tanh':
            # d(tanh) = 1 - tanh^2.
            return 1 - func_out * func_out
        elif func_name == 'sigmoid':
            # d(sigmoid) = sigmoid * (1 - sigmoid).
            return func_out * (1 - func_out)

    @staticmethod
    def __loss(a_out, a):
        """
        :param a_out: network output.
        :param a: desired output.
        :return: sum of squared difference normalized.
        """
        return np.sum(np.square(a_out - a)) / a.shape[0]

    def __d_out(self, a_h, a_o, a):
        """
        :param a_h: hidden output.
        :param a_o: net_out.
        :param a: desired out.
        :return: d(Loss) / d(W_out(i, k)) = SUM_i((d(Loss) / d(a_o(i)) * (d(a_o(i)) / d(W_out(i, k)).
                 (d(a_o(i)) / d(W_out(i, k)) != 0 if and only if i == k because of z = SUM(a_h(i) * W_out(j, i) =>
                 d(Loss) / d(W_out(i, k)) = (d(Loss) / d(a_o(k)) * (d(a_o(k)) / d(W_out(i, k))
                                          = (2 * (a_o(k) - a(k))) * ((d(activation(z) / d(z)) * (d(z) / d(W_out(i, k)))
                                          = (2 * (a_o(k) - a(k))) * a_h(i) * (d(activation(z)) / d(z))
        """
        d_loss = np.dot(a_h.T, (2.0 * (a_o - a) * self.__d_activation(a_o, self.out_func)))
        return self.alpha * d_loss / a.shape[0]

    def _d_hidden(self, X, a_h, a_o, a):
        """
        :param X: input.
        :param a_h: hidden output.
        :param a_o: net_out.
        :param a: desired out.
        :return: d(Loss) / d(W_h(i, k))   = SUM_p((d(Loss) / d(a_o(p))) * SUM_j((d(a_o(p)) / d(a_h(j)) * (d(a_h(j)) / d(W_h(i, k))))
                                          = SUM_p((d(Loss) / d(a_o(p))) * (d(a_o(p)) / d(a_h(k)) * (d(a_h(k)) / d(W_h(i, k)))
                 d(Loss) / d(a_o(p))      = 2 * (a_o(p) - a(p))
                 d(a_o(p)) / d(a_h(k))    = ((d(activation_out(z) / d(z)) * W_out(k, p) where z = a_o(p)
                 d(a_h(k)) / d(W_h(i, k)) = X(i) * (d(activation_hidden(z)) / d(z)) where z = a_h(k)
        """
        # W_out[1:] because first row is bias.
        d_loss = np.dot(X.T, np.dot(2.0 * (a_o - a) * self.__d_activation(a_o, self.out_func), self.W_out[1:].T) *
                                                      self.__d_activation(a_h, self.hidden_func))
        return self.alpha * d_loss / a.shape[0]

    @staticmethod
    def __add_bias(X):
        """
        :param X: input.
        :return: concatenate ones to input to get bias term.
        """
        bias = np.ones((X.shape[0], 1))
        return np.concatenate((bias, X), axis=1)

    def __forward_backward_prop(self, X, y):
        """
        :param X: input.
        :param y: ground truth.
        :return: updated weights.
        """
        # multiply input by weights.
        z_h = np.dot(X, self.W_h)
        # apply activation function.
        a_h = self.__activation(z_h, self.hidden_func)

        # add 1 to hidden layer to get bias term.
        a_h_b = self.__add_bias(a_h)

        # multiply previous layer output by weights of current layer.
        z_o = np.dot(a_h_b, self.W_out)
        # apply activation function.
        a_o = self.__activation(z_o, self.out_func)

        # calculate derivatives.
        d_out = self.__d_out(a_h_b, a_o, y)
        d_hidden = self._d_hidden(X, a_h, a_o, y)

        # update weights using calculated gradients.
        self.W_out -= d_out
        self.W_h -= d_hidden

    def fit(self, X, y):
        """
        :param X: input. shape = (number_of_examples, features).
        :param y: output. shape = (number_of_examples, classes).
        """
        # add 1 to input layer to get bias term.
        X = self.__add_bias(X)

        # multiplying by sqrt(2.0 / input_shape_size) for vanishing exploding gradients. (Andrew Ng. deep learning course).
        # put bias in weights.
        self.W_h = np.random.randn(X.shape[1], self.nn_size) * np.sqrt(2.0 / X.shape[1])
        self.W_out = np.random.randn(self.nn_size + 1, y.shape[1]) * np.sqrt(2.0 / (self.nn_size + 1))
        batch_iters = int(X.shape[0] / self.batch_size)
        batch_rem = X.shape[0] - self.batch_size * batch_iters

        for i in range(self.epochs):
            # update weights in every batch.
            for j in range(batch_iters):
                x_batch = X[j * self.batch_size : (j + 1) * self.batch_size, :]
                y_batch = y[j * self.batch_size : (j + 1) * self.batch_size, :]
                self.__forward_backward_prop(x_batch, y_batch)
            x_batch = X[-batch_rem:]
            y_batch = y[-batch_rem:]
            self.__forward_backward_prop(x_batch, y_batch)
            # print loss in end of epoch.
            if i % 100 == 0:
                a_o = self.predict_prob(X)
                print("Loss = " + str(self.__loss(a_o, y)))

    def predict_prob(self, X):
        """
        :param X: input to predict.
        :return: output vector of probabilities.
        """
        z_h = np.dot(X, self.W_h)
        a_h = self.__activation(z_h, self.hidden_func)

        a_h_b = self.__add_bias(a_h)
        z_o = np.dot(a_h_b, self.W_out)
        a_o = self.__activation(z_o, self.out_func)
        return a_o

    def predict(self, X):
        """
        :param X: input to predict.
        :return: class that has max probability.
        """
        a_o = self.predict_prob(X)
        max_value = max(a_o)
        max_index = np.where(max_value == a_o)[0]
        print("Max probability is class " + str(max_index) + " with probability " + str(max_value))
