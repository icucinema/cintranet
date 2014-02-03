import QtQuick 2.0

Rectangle {
    id: borderRect
    width: 400
    height: 400

    color: "#cccccc"
    border.width: 5
    border.color: "#333333"
    radius: 10
    property alias searchModel: searchListView.model
    property alias selectedModel: selectListView.model

    function focusDateInput() {
        dateInput.focus = true;
    }
    function resetDateInput() {
        var d = new Date();
        var day = d.getDate().toString();
        if (day.length < 2) day = '0' + day;
        var month = (d.getMonth() + 1).toString();
        if (month.length < 2) month = '0' + month;
        dateInput.text = [day, month, d.getFullYear()].join('/');
        updateEventListing(dateInput.text);
    }
    signal updateEventListing(string date);
    signal cancelClicked();
    signal confirmClicked();

    Text {
        renderType: Text.NativeRendering
        id: titleLabel
        text: qsTr("Selecting Events")
        anchors.top: parent.top
        anchors.topMargin: 20
        anchors.left: parent.left
        anchors.leftMargin: 20
        font.bold: true
        font.pixelSize: 20
    }

    TextInput {
        renderType: TextInput.NativeRendering
        id: dateInput
        height: 20
        text: qsTr("")
        anchors.top: parent.top
        anchors.topMargin: 69
        anchors.left: parent.left
        anchors.leftMargin: 70
        anchors.right: parent.right
        anchors.rightMargin: 20
        font.pixelSize: 16
        font.bold: false
        cursorVisible: true

        Keys.onEscapePressed: cancelClicked()
        Keys.onReturnPressed: updateEventListing(dateInput.text)
        Keys.onEnterPressed: updateEventListing(dateInput.text)
    }

    Text {
        renderType: Text.NativeRendering
        id: dateLabel
        text: qsTr("Date:")
        anchors.top: parent.top
        anchors.topMargin: 67
        anchors.left: parent.left
        anchors.leftMargin: 20
        font.bold: true
        font.pixelSize: 16
    }

    Button {
        id: saveButton
        y: 172
        text: "Save"
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 20
        anchors.left: parent.left
        anchors.leftMargin: 20
        heightPadding: 20
        widthPadding: 40
        onClicked: {
            confirmClicked(dateInput.text)
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

    ListView {
        id: searchListView
        x: 20
        y: 139
        width: (parent.width / 2) - 20
        height: 174
        clip: true
        anchors.left: parent.left
        anchors.leftMargin: 20
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 87
        anchors.top: parent.top
        anchors.topMargin: 139
        model: ListModel {}
        delegate: Item {
            x: 5
            height: 50
            Row {
                id: searchListRow
                spacing: 10

                Rectangle {
                    width: selectListView.width - 10
                    radius: 5
                    height: 40

                    border {
                        color: "#eeeeee"
                        width: 5
                    }
                    color: "#cccccc"

                    Text {
                        x: 5
                        id: searchListText
                        renderType: Text.NativeRendering
                        text: name
                        anchors.verticalCenter: parent.verticalCenter
                        font.bold: true
                        wrapMode: Text.WordWrap
                        anchors.left: parent.left
                        anchors.leftMargin: 10
                        anchors.right: parent.right
                        anchors.rightMargin: 10
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            selectListView.model.add_item(eventId)
                        }
                    }
                }
            }
        }
    }

    ListView {
        id: selectListView
        x: 197
        width: searchListView.width
        clip: true
        anchors.right: parent.right
        anchors.rightMargin: 20
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 87
        anchors.top: parent.top
        anchors.topMargin: 139
        model: ListModel {}
        delegate: Item {
            x: 5
            height: 50
            Row {
                id: selectListRow
                spacing: 10

                Rectangle {
                    width: selectListView.width - 10
                    radius: 5
                    height: 40

                    border {
                        color: "#eeeeee"
                        width: 5
                    }
                    color: "#cccccc"

                    Text {
                        x: 5
                        id: selectListText
                        renderType: Text.NativeRendering
                        text: name
                        anchors.verticalCenter: parent.verticalCenter
                        font.bold: true
                        wrapMode: Text.WordWrap
                        anchors.left: parent.left
                        anchors.leftMargin: 10
                        anchors.right: parent.right
                        anchors.rightMargin: 10
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            selectListView.model.remove_item(eventId)
                        }
                    }
                }
            }
        }
    }

    Text {
        renderType: Text.NativeRendering
        id: resultsLabel
      
         x: 20
        y: 122
        text: qsTr("Results:")
        font.pixelSize: 12
    }

    Text {
        renderType: Text.NativeRendering
        id: selectedLabel
        x: parent.width / 2
        y: 122
        text: qsTr("Selected:")
        font.pixelSize: 12
    }
}
