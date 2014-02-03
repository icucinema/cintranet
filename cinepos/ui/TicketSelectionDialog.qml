import QtQuick 2.0
import "ColumnHelper.js" as ColumnHelper

Rectangle {
    id: borderRect
    width: 600
    height: 400

    color: "#cccccc"
    border.width: 5
    border.color: "#333333"
    radius: 10

    signal closeClicked();
    signal backClicked();
    signal ticketClicked(int ticketNumber);

    property string title : "Ticket Selection"

    property var ticketsModel;

    function bitsWithPadding(bits, requiredLength, separator) {
        var newBits = [];
        for (var i = 0; i < bits.length; i++) {
            var b = bits[i].toString();
            while (b.length < requiredLength) {
                b = '0' + b;
            }
            newBits.push(b);
        }
        return newBits.join(separator);
    }

    function formatDate(isoformat) {
        var d = new Date(isoformat);
        return bitsWithPadding([d.getDate(), d.getMonth()+1, d.getFullYear()], 2, '/');
    }
    function formatTime(isoformat) {
        var d = new Date(isoformat);
        return bitsWithPadding([d.getHours(), d.getMinutes()], 2, ':');
    }

    Text {
        renderType: Text.NativeRendering
        id: titleLabel
        text: title
        anchors.top: parent.top
        anchors.topMargin: 20
        anchors.left: parent.left
        anchors.leftMargin: 20
        font.bold: true
        font.pixelSize: 20
    }

    Button {
        id: backButton
        x: 469
        y: 176
        text: "Back"
        anchors.left: parent.left
        anchors.leftMargin: 20
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 20
        widthPadding: 40
        heightPadding: 20
        onClicked: {
            backClicked()
        }
    }

    Button {
        id: closeButton
        x: 469
        y: 176
        text: "Close"
        anchors.right: parent.right
        anchors.rightMargin: 20
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 20
        widthPadding: 40
        heightPadding: 20
        onClicked: {
            closeClicked()
        }
    }

    ListView {
        clip: true
        id: ticketListView
        anchors.right: parent.right
        anchors.rightMargin: 20
        anchors.left: parent.left
        anchors.leftMargin: 20
        anchors.bottom: backButton.top
        anchors.bottomMargin: 6
        anchors.top: titleLabel.bottom
        anchors.topMargin: 6
        delegate: Item {

            function altColor(i) {
                var colors = [ "#bebebe", "#b7b7b7" ];
                return colors[i];
            }

            Rectangle {
                id: background
                width:  parent.width + 15
                height: parent.height
                color: altColor(index%2)
            }
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    ticketClicked(id);
                }
            }

            width: parent.width - 15

            x: 5
            height: 40
            Row {
                anchors.verticalCenter: parent.verticalCenter
                id: ticketListRow
                spacing: 10

                Text {
                    renderType: Text.NativeRendering
                    text: id
                    font.bold: true
                    anchors.verticalCenter: parent.verticalCenter
                    width: 30
                }

                Text {
                    renderType: Text.NativeRendering
                    text: punter_name
                    font.bold: true
                    anchors.verticalCenter: parent.verticalCenter
                    width: 200
                }

                Text {
                    renderType: Text.NativeRendering
                    text: ticket_type_name
                    font.bold: false
                    anchors.verticalCenter: parent.verticalCenter
                    width: 180
                }

                Text {
                    renderType: Text.NativeRendering
                    text: formatDate(timestamp) + " " + formatTime(timestamp)
                    font.bold: false
                    anchors.verticalCenter: parent.verticalCenter
                    width: 100
                }
            }
        }
        model: ticketsModel
    }
}
