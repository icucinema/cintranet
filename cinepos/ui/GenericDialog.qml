import QtQuick 2.0

Rectangle {
    id: borderRect
    width: 400
    height: bodyLabel.anchors.topMargin + bodyLabel.height + bodyLabel.anchors.bottomMargin + 10
    //height: 300

    color: "#cccccc"
    border.width: 5
    border.color: "#333333"
    radius: 10

    property var info: ({
                            title: "Dialog Title",
                            message: "A really long message that will wrap, blah, blah, blah, blah, blah, blah, blah, blah, blah, blah, blah, blah, blah, blah, blah, blah, blah, blah",
                            button: "OK",
                            button_target: "",
                            type: ""
                        });

    signal buttonClicked(string nextState);

    Text {
        id: titleLabel
        text: info.title
        anchors.top: parent.top
        anchors.topMargin: 20
        anchors.left: parent.left
        anchors.leftMargin: 20
        font.bold: true
        font.pixelSize: 20
    }

    Button {
        id: closeButton
        y: 236
        text: info.button
        anchors.left: parent.left
        anchors.leftMargin: 20
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 20
        anchors.right: parent.right
        anchors.rightMargin: 20
        widthPadding: 10
        heightPadding: 10
        onClicked: {
            buttonClicked(info.button_target)
        }
    }

    Text {
        id: bodyLabel
        text: info.message
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 87
        anchors.top: parent.top
        anchors.topMargin: 67
        anchors.right: parent.right
        anchors.rightMargin: 20
        anchors.left: parent.left
        anchors.leftMargin: 20
        font.pixelSize: 18
    }
}
