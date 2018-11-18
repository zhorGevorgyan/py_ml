import numpy as np


class LogisticRegression:
    def __init__(self, number_of_iterations, learning_rate):
        self.W = np.zeros((1, 1))
        self.num_iters = number_of_iterations
        self.alpha = learning_rate

    @staticmethod
    def __activation_func(z):
        """
        :param z: dot(X, W)
        :return: sigmoid(z) because we want probability of output. e.g. y_hat can be between [0, 1]
        """
        return 1.0 / (1 + np.exp(-z))

    @staticmethod
    def __loss(y_hat, y):
        """
        :param y_hat: neuron output
        :param y: desired output
        :return: y_hat = P(y = 1 | x) => P(y = 0 | x) = 1 - y_hat =>
                 P = (y_hat^y) * ((1 - y_hat)^(1 - y))
                 choosing loss as -Log(P) to maximize we get convex function.
        """
        return np.mean(-y * np.log(y_hat) - (1 - y) * np.log(1 - y_hat))

    @staticmethod
    def __d_loss(X, y_hat, y):
        """
        :param X: input
        :param y_hat: neuron output
        :param y: desired output
        :return: d(L) / d(Wi) = (d(L) / d(y_hat)) * (d(y_hat) / d(Wi)) =
                                (-y / y_hat + (1 - y) / (1 - y_hat)) * (d(sigmoid(sum(Wi * xi)) / d(Wi)) =
                                ((y * (y_hat - 1) + (1 - y) * y_hat) / (y_hat * (1 - y_hat))) * (xi * y_hat * (1 - y_hat)) =
                                xi * (y_hat - y)
        """
        return np.dot(X.T, y_hat - y) / y.size

    @staticmethod
    def __add_bias(X):
        """
        :param X: input
        :return: concatenate ones to input to get bias term.
        """
        bias = np.ones((X.shape[0], 1))
        return np.concatenate((bias, X), axis=1)

    def fit(self, X, y):
        """
        :param X: input
        :param y: desired outputx
        :return: weight matrix
        """
        X = self.__add_bias(X)
        self.W = np.zeros(X.shape[1])
        for i in range(self.num_iters):
            z = np.dot(X, self.W)
            y_hat = self.__activation_func(z)
            gradient = self.__d_loss(X, y_hat, y)
            self.W -= self.alpha * gradient

            if i % 100 == 0:
                z = np.dot(X, self.W)
                y_hat = self.__activation_func(z)
                print ("Loss = " + str(self.__loss(y_hat, y)))

    def predict_prob(self, X):
        """
        :param X: input
        :return: y_hat
        """
        return self.__activation_func(np.dot(X, self.W))

    def predict(self, X, threshold=0.5):
        """
        :param X: input
        :param threshold: threshold y_hat
        :return: y_hat >= threshold
        """
        return self.predict_prob(X) >= threshold