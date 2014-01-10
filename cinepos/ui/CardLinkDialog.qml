import QtQuick 2.0

Rectangle {
    id: borderRect
    width: 400
    height: 190

    color: "#cccccc"
    border.width: 5
    border.color: "#333333"
    radius: 10

    signal linkClicked(string cid);
    signal cancelClicked();

    function focusCidInput() {
        cidInput.focus = true;
    }
    function clearCidInput() {
        cidInput.text = "";
    }

    Text {
        id: titleLabel
        text: qsTr("Linking Card to CID")
        anchors.top: parent.top
        anchors.topMargin: 20
        anchors.left: parent.left
        anchors.leftMargin: 20
        font.bold: true
        font.pixelSize: 20
    }

    TextInput {
        id: cidInput
        height: 20
        text: qsTr("")
        anchors.top: parent.top
        anchors.topMargin: 69
        anchors.left: parent.left
        anchors.leftMargin: 60
        anchors.right: parent.right
        anchors.rightMargin: 20
        font.pixelSize: 16
        font.bold: false
        cursorVisible: true

        Keys.onEscapePressed: cancelClicked()
        Keys.onReturnPressed: linkClicked(cidInput.text)
        Keys.onEnterPressed: linkClicked(cidInput.text)
    }

    Text {
        id: cidLabel
        text: qsTr("CID:")
        anchors.top: parent.top
        anchors.topMargin: 67
        anchors.left: parent.left
        anchors.leftMargin: 20
        font.bold: true
        font.pixelSize: 16
    }

    Button {
        id: linkButton
        y: 172
        text: "Input"
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 20
        anchors.left: parent.left
        anchors.leftMargin: 20
        heightPadding: 20
        widthPadding: 40
        onClicked: {
            linkClicked(cidInput.text)
        }
    }

    Button {
        id: cancelButton
        x: 469
        y: 176
        text: "Cancel"
        anchors.right: parent.right
        anchors.rightMargin: 20
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 20
        widthPadding: 40
        heightPadding: 20
        onClicked: {
            cancelClicked()
        }
    }
}
