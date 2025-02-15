import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


class BaseSubplot:
    def __init__(self):
        pass
    
    def draw(self):
        raise Exception("Not implemented")

    def __call__(self, *args, **kwargs):
        self.draw(*args, **kwargs)


class LossSubplot(BaseSubplot):
    def __init__(self,
                 metric,
                 title="",
                 series_fmt={'training': '{}', 'validation':'val_{}'},
                 skip_first=2,
                 max_epoch=None):
        super().__init__(self)
        self.metric = metric
        self.title = title
        self.series_fmt = series_fmt
        self.skip_first = skip_first
        self.max_epoch = max_epoch
    
    def _how_many_to_skip(self, log_length, skip_first):
        if log_length < skip_first:
            return 0
        elif log_length < 2 * skip_first:
            return log_length - skip_first
        else:
            return skip_first

    def draw(self, logs):
        skip = self._how_many_to_skip(len(logs), self.skip_first)

        if self.max_epoch is not None:
            plt.xlim(1 + skip, self.max_epoch)

        for serie_label, serie_fmt in self.series_fmt.items():

            serie_metric_name = serie_fmt.format(self.metric)
            serie_metric_logs = [(log.get('_i', i + 1), log[serie_metric_name])
                                for i, log in enumerate(logs[skip:])
                                if serie_metric_name in log]

            if len(serie_metric_logs) > 0:
                xs, ys = zip(*serie_metric_logs)
                lbl = "{}: {:.4f}".format(lbl, ys[-1])
                plt.plot(xs, ys, label=lbl)

        plt.title(self.title)
        plt.xlabel('epoch')
        plt.legend()


class Plot1D(BaseSubplot):
    def __init__(self, model, X, Y):
        super().__init__(self)
        self.model = model
        self.X = X 
        self.Y = Y

    def predict(self, model, X):
        # e.g. model(torch.fromnumpy(X)).detach().numpy()
        return model.predict(X)

    def draw(self, *args, **kwargs):
        plt.plot(self.X, self.Y, 'r.', label="Ground truth")
        plt.plot(self.X, self.predict(self.model, self.X), '-', label="Model")
        plt.title("Prediction")
        plt.legend()


class Plot2d(BaseSubplot):
    def __init__(self, model, X, Y, valiation_data=(None, None), h=0.02, margin=0.25):
        super().__init__()

        self.model = model
        self.X = X 
        self.Y = Y
        self.X_test, self.Y_test = valiation_data

        # add size assertions

        self.cm_bg = plt.cm.RdBu
        self.cm_points = ListedColormap(['#FF0000', '#0000FF'])

        h = .02  # step size in the mesh
        x_min = X[:, 0].min() - margin
        x_max = X[:, 0].max() + margin

        y_min = X[:, 1].min() - margin
        y_max = X[:, 1].max() + margin

        self.xx, self.yy = np.meshgrid(
            np.arange(x_min, x_max, h),
            np.arange(y_min, y_max, h))
        

    def _predict_pytorch(self, model, x_numpy):
        import torch
        x = torch.from_numpy(x_numpy).float()
        return model(x).softmax(dim=1).detach().numpy()

    def predict(self, model, X):
        # e.g. model(torch.fromnumpy(X)).detach().numpy()
        return model.predict(X)

    def draw(self, *args, **kwargs):
        Z = self._predict_pytorch(self.model, np.c_[self.xx.ravel(), self.yy.ravel()])[:, 1]
        Z = Z.reshape(self.xx.shape)
        plt.contourf(self.xx, self.yy, Z, cmap=self.cm_bg, alpha=.8)
        plt.scatter(self.X[:, 0], self.X[:, 1], c=self.Y, cmap=self.cm_points)
        if self.X_test is not None:
            plt.scatter(self.X_test[:, 0], self.X_test[:, 1], c=self.Y_test, cmap=self.cm_points, alpha=0.3)
