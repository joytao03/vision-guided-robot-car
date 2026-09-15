# Third-Party Dependencies and References

The reconstruction uses public libraries through their APIs. No third-party source files or copied tutorial snippets are included in this implementation.

| Dependency | Use | Upstream license and source |
| --- | --- | --- |
| OpenCV (`opencv-python-headless`) | BGR-to-grayscale conversion, Gaussian blur, thresholding, drawing, image I/O | OpenCV 4.5+ uses [Apache 2.0](https://opencv.org/license/); [Python packaging repository](https://github.com/opencv/opencv-python) provides packaging and bundled-component notices |
| NumPy | Image arrays, scanline runs, geometry | [BSD 3-Clause](https://numpy.org/doc/stable/license.html) |
| pytest (test extra) | Automated validation | [MIT](https://github.com/pytest-dev/pytest/blob/main/LICENSE) |
| setuptools (build only) | Python packaging | [MIT](https://github.com/pypa/setuptools/blob/main/LICENSE) |

API references: [OpenCV image thresholding](https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html) and [image smoothing](https://docs.opencv.org/4.x/d4/d13/tutorial_py_filtering.html).

The scanline pairing, validity checks, fixtures, tests, and layer integration are newly written for this reconstruction. They are not recovered code from the original school project. The course-concept image has separate [provenance notes](assets/concepts/README.md). Future source reuse should record the exact upstream source, license, and modifications here and retain any required notices.

The steering PID, anti-windup logic, perception adapter, and controller tests are newly written for this repository using the standard discrete PID formulation. No external PID source code is copied and no additional runtime dependency is required.
