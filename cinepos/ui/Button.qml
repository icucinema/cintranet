import QtQuick 2.0

Rectangle {
    width: textBit.width + 10 + widthPadding
    height: textBit.height + 6 + heightPadding
    radius: 5
    property alias text: textBit.text
    property int widthPadding: 0
    property int heightPadding: 0
    signal clicked

    border {
        color: "#eeeeee"
        width: 5
    }
    color: "#cccccc"

    Text {
        renderType: Text.NativeRendering
        x: 5
        y: 3
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        id: textBit
        text: "Blah blah blah blah blah"
        font.pixelSize: 20
    }

    MouseArea {
        id: clickArea
        anchors.fill: parent
        onClicked: {
            parent.clicked()
        }
    }
}
