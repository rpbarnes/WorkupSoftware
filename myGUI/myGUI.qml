import QtQuick 2.2

Rectangle {
    width: 360
    height: 360

    Grid {
        id: grid1
        x: 181
        y: 13
        width: 154
        height: 261

        TextEdit {
            id: textEdit1
            width: 80
            height: 20
            text: qsTr("Text Edit")
            font.pixelSize: 12
        }

        TextEdit {
            id: textEdit2
            width: 80
            height: 20
            text: qsTr("Text Edit")
            font.pixelSize: 12
        }

        TextEdit {
            id: textEdit3
            width: 80
            height: 20
            text: qsTr("Text Edit")
            font.pixelSize: 12
        }

        TextEdit {
            id: textEdit4
            width: 80
            height: 20
            text: qsTr("Text Edit")
            font.pixelSize: 12
        }
    }

    Image {
        id: image1
        x: 8
        y: 13
        width: 149
        height: 147
        fillMode: Image.PreserveAspectFit
        source: "qrc:/qtquickplugin/images/template_image.png"
    }
}

