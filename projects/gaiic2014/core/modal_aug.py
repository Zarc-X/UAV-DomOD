from typing import Dict, Sequence, Tuple

import cv2
import numpy as np
from mmcv.transforms import BaseTransform
from mmcv.transforms.utils import cache_randomness
from mmdet.registry import TRANSFORMS


def _cast_like(img: np.ndarray, dtype: np.dtype) -> np.ndarray:
    """Cast array to original dtype with safe clipping for integer types."""
    if np.issubdtype(dtype, np.integer):
        info = np.iinfo(dtype)
        img = np.clip(img, info.min, info.max)
    return img.astype(dtype)


@TRANSFORMS.register_module()
class RandomBrightnessContrastByKey(BaseTransform):
    """Apply brightness/contrast jitter to one modality key only."""

    def __init__(
        self,
        key: str = "img",
        prob: float = 0.5,
        brightness_delta: float = 24.0,
        contrast_range: Tuple[float, float] = (0.8, 1.2),
    ) -> None:
        assert 0.0 <= prob <= 1.0
        assert brightness_delta >= 0.0
        assert contrast_range[0] > 0.0 and contrast_range[1] >= contrast_range[0]
        self.key = key
        self.prob = prob
        self.brightness_delta = brightness_delta
        self.contrast_range = contrast_range

    @cache_randomness
    def _sample_params(self) -> Tuple[bool, float, float]:
        apply = np.random.rand() < self.prob
        alpha = np.random.uniform(*self.contrast_range)
        beta = np.random.uniform(-self.brightness_delta, self.brightness_delta)
        return apply, alpha, beta

    def transform(self, results: Dict) -> Dict:
        if self.key not in results:
            return results
        apply, alpha, beta = self._sample_params()
        if not apply:
            return results

        src = results[self.key]
        dst = src.astype(np.float32) * alpha + beta
        results[self.key] = _cast_like(dst, src.dtype)
        return results


@TRANSFORMS.register_module()
class RandomGaussianNoiseByKey(BaseTransform):
    """Add Gaussian noise to one modality key only."""

    def __init__(
        self,
        key: str = "img",
        prob: float = 0.4,
        std_range: Tuple[float, float] = (3.0, 12.0),
    ) -> None:
        assert 0.0 <= prob <= 1.0
        assert std_range[0] >= 0.0 and std_range[1] >= std_range[0]
        self.key = key
        self.prob = prob
        self.std_range = std_range

    @cache_randomness
    def _sample_params(self) -> Tuple[bool, float]:
        apply = np.random.rand() < self.prob
        std = np.random.uniform(*self.std_range)
        return apply, std

    def transform(self, results: Dict) -> Dict:
        if self.key not in results:
            return results
        apply, std = self._sample_params()
        if not apply or std <= 0:
            return results

        src = results[self.key]
        noise = np.random.normal(0.0, std, size=src.shape).astype(np.float32)
        dst = src.astype(np.float32) + noise
        results[self.key] = _cast_like(dst, src.dtype)
        return results


@TRANSFORMS.register_module()
class RandomGaussianBlurByKey(BaseTransform):
    """Apply Gaussian blur to one modality key only."""

    def __init__(
        self,
        key: str = "tir",
        prob: float = 0.3,
        kernel_sizes: Sequence[int] = (3, 5),
        sigma_range: Tuple[float, float] = (0.1, 1.2),
    ) -> None:
        assert 0.0 <= prob <= 1.0
        assert len(kernel_sizes) > 0
        assert sigma_range[0] >= 0.0 and sigma_range[1] >= sigma_range[0]
        self.key = key
        self.prob = prob
        self.kernel_sizes = tuple(int(k) for k in kernel_sizes)
        self.sigma_range = sigma_range

    @cache_randomness
    def _sample_params(self) -> Tuple[bool, int, float]:
        apply = np.random.rand() < self.prob
        ksize = int(np.random.choice(self.kernel_sizes))
        if ksize % 2 == 0:
            ksize += 1
        sigma = float(np.random.uniform(*self.sigma_range))
        return apply, max(1, ksize), sigma

    def transform(self, results: Dict) -> Dict:
        if self.key not in results:
            return results
        apply, ksize, sigma = self._sample_params()
        if not apply:
            return results

        src = results[self.key]
        dst = cv2.GaussianBlur(src, (ksize, ksize), sigmaX=sigma, sigmaY=sigma)
        results[self.key] = dst
        return results


@TRANSFORMS.register_module()
class RandomEdgeEnhanceByKey(BaseTransform):
    """Apply edge enhancement (unsharp mask) to one modality key only."""

    def __init__(
        self,
        key: str = "tir",
        prob: float = 0.3,
        strength_range: Tuple[float, float] = (0.4, 1.0),
        sigma_range: Tuple[float, float] = (0.8, 2.0),
    ) -> None:
        assert 0.0 <= prob <= 1.0
        assert strength_range[0] >= 0.0 and strength_range[1] >= strength_range[0]
        assert sigma_range[0] > 0.0 and sigma_range[1] >= sigma_range[0]
        self.key = key
        self.prob = prob
        self.strength_range = strength_range
        self.sigma_range = sigma_range

    @cache_randomness
    def _sample_params(self) -> Tuple[bool, float, float]:
        apply = np.random.rand() < self.prob
        strength = float(np.random.uniform(*self.strength_range))
        sigma = float(np.random.uniform(*self.sigma_range))
        return apply, strength, sigma

    def transform(self, results: Dict) -> Dict:
        if self.key not in results:
            return results
        apply, strength, sigma = self._sample_params()
        if not apply:
            return results

        src = results[self.key]
        src_f = src.astype(np.float32)
        blur = cv2.GaussianBlur(src_f, (0, 0), sigmaX=sigma, sigmaY=sigma)
        dst = src_f + strength * (src_f - blur)
        results[self.key] = _cast_like(dst, src.dtype)
        return results