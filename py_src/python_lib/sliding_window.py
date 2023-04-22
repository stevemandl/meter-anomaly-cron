import numpy as np
from scipy.stats import t

class SlidingWindow:
    def __init__(self, k: int):
        """
        Sliding window outlier detection for point-wise outliers. Adapted from https://doi.org/10.1155/2014/879736.

        Arguments
        k: the number of left neighbors to use
        confidence: 0 <= confidence <= 1, how confident you want the detected outliers to be
        """
        self.k = k
        self.regressor = None
        self.regressor_loss = -1

    def attach_regressor(self, regressor = None, loss = 0):
        """
        Arguments
        regressor: (d*k)-dimensional vector -> d-dimensional vector
        loss: regressor loss metric, must be >= 0
        """
        self.regressor = regressor
        self.regressor_loss = loss

    def slide_window(self, data, confidence = 0.99):
        # TODO: refactor margins
        if self.regressor == None:
            raise RuntimeError("Regressor not attached")
        if self.regressor_loss <= 0:
            raise RuntimeError("No regressor loss")
        d, n = data.shape
        if self.k >= n:
            raise RuntimeError("n has to be > k")
        
        pci_upper = np.ndarray((d, n), dtype=np.dtype(float))
        pci_upper[:, :self.k] = np.inf
        pci_lower = np.ndarray((d, n), dtype=np.dtype(float))
        pci_lower[:, :self.k] = -np.inf

        conf = t.ppf(confidence, 2*self.k - 1)

        regressor_output = np.ndarray((d, n), dtype=np.dtype(float))
        regressor_output[:, :self.k] = np.inf

        outlier = np.ndarray((n, ), dtype=np.dtype(bool))

        for i in range(n - self.k):
            inp = data[:, i:i+self.k]
            out = self.regressor(inp.flatten())
            std_dev = np.sqrt(np.sum(np.square(inp - np.mean(inp))) / n) # std dev of the k neighbors
            pci_margin = conf*max(std_dev, 1)*self.regressor_loss*np.sqrt(1 + 1/(2*self.k)) # defined in the paper, with some addtional modifications
            pci_up = out + pci_margin
            pci_down = out - pci_margin
            pci_upper[:, i+self.k] = pci_up
            pci_lower[:, i+self.k] = pci_down
            regressor_output[:, i+self.k] = out
            if (data[:, i+self.k] > pci_up).all() or (data[:, i+self.k] < pci_down).all():
                outlier[i+self.k] = True
            else:
                outlier[i+self.k] = False

        return regressor_output, pci_lower, pci_upper, outlier
    
    def margins(self, data, confidence = 0.99):
        _, pci_lower, pci_upper, _ = self.slide_window(data, confidence)
        return pci_lower, pci_upper
    
    def regression_line(self, data, confidence = 0.99):
        ret, _, _, _ = self.slide_window(data, confidence)
        return ret
    
    def outliers(self, data, confidence = 0.99):
        _, _, _, ret = self.slide_window(data, confidence)
        return ret
    
    def generate_training_data(self, data: list):
        """
        Generates a data matrix of all possible sliding windows of length k in data.

        Arguments
        data: (d x n)-dimensional ndarray, d time-series with n evenly spaced observations, no time index

        Returns
        features: (n - k - 1) x d x k dimensional
        labels: (n - k - 1) x d dimensional
        """
        d, n = data.shape
        if self.k >= n:
            raise RuntimeError("n has to be > k")
        features = np.ndarray((n - self.k - 1, d, self.k))
        labels = np.ndarray((n - self.k - 1, d))
        for i in range(n - self.k - 1):
            features[i] = data[:, i:i+self.k].reshape((d, self.k))
            labels[i] = data[:, i+self.k].reshape((d,))
        return features, labels