import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Window 2.0

ApplicationWindow {
    title: qsTr("Hello World")
    width: 640
    height: 480

    menuBar: MenuBar {
        Menu {
            title: qsTr("File")
            MenuItem {
                text: qsTr("Exit")
                onTriggered: Qt.quit();
            }
        }
    }

    Button {
        text: qsTr("Switch Temp")
        checkable: true
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
    }

    TextInput {
        id: celsiusText
        x: 99
        y: 159
        width: 80
        height: 20
        text: qsTr("Celsius")
        font.pixelSize: 12
    }

    TextEdit {
        id: farenheitText
        x: 419
        y: 165
        width: 80
        height: 20
        text: qsTr("Farenheit")
        font.pixelSize: 12
    }
}
