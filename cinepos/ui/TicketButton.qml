import QtQuick 2.0

Rectangle {
    id: wrappingRect
    width: 300
    height: 120
    color: "#00000000"
    property alias text: text1.text
    property alias backgroundColor: borderedRect.color
    property alias textColor: text1.color
    property alias border: borderedRect.border
    signal clicked()

    Rectangle {
        x: border.width
        y: border.width
        id: borderedRect
        color: "#ff0000"
        radius: 5

        width: wrappingRect.width - 2 * border.width
        height: wrappingRect.height - 2 * border.width

        border.color: "#910000"
        border.width: 5

        Text {
            renderType: Text.NativeRendering
            id: text1
            text: qsTr("Text")
            anchors.right: parent.right
            anchors.rightMargin: 0
            anchors.left: parent.left
            anchors.leftMargin: 0
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 5
            wrapMode: Text.WordWrap
            style: Text.Normal
            font.pixelSize: 20
            horizontalAlignment: Text.AlignHCenter
        }

        MouseArea {
            anchors.fill: parent
            onClicked: wrappingRect.clicked()
        }
    }
}
