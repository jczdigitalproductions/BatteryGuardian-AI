import unittest
from ml.synthetic import generate
from ml.features import WINDOW, windows_from_samples
from batteryguardian.core import Sample, analyze
from ml.model import BatteryNet
import torch

class MLTests(unittest.TestCase):
    def test_shape_and_finiteness(self):
        x,y=generate(24)
        self.assertEqual(x.shape,(24,8,4))
        self.assertEqual(len(y),24)
        self.assertTrue((abs(x)<=8).all())
    def test_model_shape(self):
        self.assertEqual(tuple(BatteryNet()(torch.zeros(3,8,4)).shape),(3,))
    def test_safety_independent(self):
        samples=[Sample(str(i),3.7,2,65,50) for i in range(WINDOW)]
        self.assertEqual(analyze(samples)['status'],'critical')
        self.assertEqual(windows_from_samples(samples).shape,(1,8,4))
if __name__=='__main__':unittest.main()
