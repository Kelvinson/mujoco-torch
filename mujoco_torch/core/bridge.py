from mujoco_py import MjBatchRenderer
import torch
import pycuda.driver as cuda


class MjCudaRender(object):
    def __init__(self, img_width, img_height):
        self.img_width = img_width
        self.img_height = img_height
        self.batch_renderer = MjBatchRenderer(img_width, img_height,
                                              use_cuda=True)

    def get_cuda_tensor(self, sim, read_img=False):
        self.batch_renderer.render(sim)
        self.batch_renderer.map()
        torch_img = torch.cuda.ByteTensor(self.img_width, self.img_height, 3)
        torch_pointer = torch_img.data_ptr()

        render_pointer = self.batch_renderer._cuda_rgb_ptr
        cuda.memcpy_dtod(torch_pointer, render_pointer,
                         3*self.img_width*self.img_height)
        true_img = None
        if read_img:
            true_img = self.batch_renderer.read()[0][0]
        self.batch_renderer.unmap()
        return torch_img, true_img
