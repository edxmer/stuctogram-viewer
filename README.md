# Structogram viewer
## Demo
*Starting the program:*
![A GIF demonstration of opening up the Structogram viewer.](media/1.gif) <br><br><hr>
*Instant updates when saving file*
![A GIF demonstration of saving a file, and the Structogram viewer updating accordingly.](media/2.gif)


## Usage
### Dependencies:
```sh
python3 pip install pywebview
```
### Run project
```sh
python3 main.py (path-to-structogram)
```

## Pseudo-code specifications
>The `stukis/demo/demo.stuki` file contains a demo code that contains all language features.

Note: White spaces are ignored.

---
### caption
Set the caption of the structogram
```
caption <caption>
```

---
### statements
```
x:=1
f(y)
hello
[
    x:="hello
    there"
]
```
<img src="media/spec-1.png" alt="generated structogram" width="400"/><br>
Basically anything that is not something else

---
### if-else
```
if <condition>
    <block>
else
    <block>
end
```
<img src="media/spec-2.png" alt="generated structogram" width="400"/><br>

---
### while
```
while <condition>
    <block>
end
```
<img src="media/spec-3.png" alt="generated structogram" width="400"/><br>

---
### do-while
```
do
    <block>
while <condition>
```
<img src="media/spec-4.png" alt="generated structogram" width="400"/><br>

---
### switch-case
```
switch
    case <condition>
        <block>
    case <condition>
        <block>
    case <condition>
        <block>
    ...
end
```
<img src="media/spec-5.png" alt="generated structogram" width="400"/><br>


---
### comments
```
# Code-only comment
// This is a displayed comment
/*
This is a
multiline comment
*/
```
<img src="media/spec-6.png" alt="generated structogram" width="400"/><br>

### statement text formatting
```
§* BOLD *§
§# italic #§
§_ underline _§
you can also add extra §s §s  spaces
§t §t or §t §t tabs
line §n break
```
<img src="media/spec-7.png" alt="generated structogram" width="400"/><br>