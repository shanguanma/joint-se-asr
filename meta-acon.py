import torch
from torch import nn

class MetaAconC(nn.Module):
    r""" ACON activation (activate or not).
    # MetaAconC: (p1*x-p2*x) * sigmoid(beta*(p1*x-p2*x)) + p2*x, beta is generated by a small network
    # according to "Activate or Not: Learning Customized Activation" <https://arxiv.org/pdf/2009.04759.pdf>.
    """
    def __init__(self, width, r=16):
        super().__init__()
        self.fc1 = nn.Conv1d(width, max(r,width//r), kernel_size=1, stride=1, bias=True)
        self.bn1 = nn.BatchNorm1d(max(r,width//r))
        
        self.fc2 = nn.Conv1d(max(r,width//r), width, kernel_size=1, stride=1, bias=True)
        self.bn2 = nn.BatchNorm1d(width)
        
        self.p1 = nn.Parameter(torch.randn(1, width, 1))
        self.p2 = nn.Parameter(torch.randn(1, width, 1))

        self.sigmoid = nn.Sigmoid()

    def forward(self, x, **kwargs):
       
        x = x.transpose(1, 2) # BxTxF -> BxFxT
        
        beta = self.sigmoid(self.bn2(self.fc2(self.bn1(self.fc1(x.mean(dim=2, keepdims=True))))))
        
        a = self.p1 * x - self.p2 * x
        b = self.sigmoid( beta * (self.p1 * x - self.p2 * x))
        c = self.p2 * x
        return (a * b + c).transpose(1,2)
