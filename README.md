# labeler
A object labeling tool built by tkinter.

![image](https://user-images.githubusercontent.com/4820492/38595834-880fa11a-3d80-11e8-81e3-7e15586d573b.png)

## Usage

```
$ python main.py
```

Output format

```
# n_frame: frame index
# class_ind: label class index
# p1: top-left coordinate
# mv_pt: bottom-right coordinate

results = {
    n_frame: [
        (class_ind, p1, mv_pt), ...
    ], ...
}
```
