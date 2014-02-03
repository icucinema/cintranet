import QtQuick 2.0

Rectangle {
    id: borderRect
    width: 400
    height: 300

    color: "#cccccc"
    border.width: 5
    border.color: "#333333"
    radius: 10

    signal closeClicked
    signal viewTicketClicked
    signal printReportClicked
    signal viewTicketsForPunterClicked
    signal viewLastSoldTicketsClicked

    Text {
        renderType: Text.NativeRendering
        id: titleLabel
        text: qsTr("Management Menu")
        anchors.top: parent.top
        anchors.topMargin: 20
        anchors.left: parent.left
        anchors.leftMargin: 20
        font.bold: true
        font.pixelSize: 20
    }

    Button {
        id: closeButton
        x: 296
        y: 236
        text: "Close"
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 20
        anchors.right: parent.right
        anchors.rightMargin: 20
        widthPadding: 10
        heightPadding: 10
        onClicked: {
            closeClicked()
        }
    }

    Button {
        id: viewTicketButton
        y: 61
        text: "View ticket information"
        heightPadding: 5
        anchors.right: parent.right
        anchors.rightMargin: 20
        anchors.left: parent.left
        anchors.leftMargin: 20
        onClicked: {
            viewTicketClicked()
        }
    }

    Button {
        id: printReportButton
        text: "Print sales report"
        heightPadding: 5
        anchors.right: parent.right
        anchors.rightMargin: 20
        anchors.left: parent.left
        anchors.leftMargin: 20
        anchors.top: viewLastSoldTicketsButton.bottom
        anchors.topMargin: 10
        onClicked: {
            printReportClicked()
        }
    }

    Button {
        id: viewTicketsForPunterButton
        x: -2
        y: 1
        text: "View tickets for customer"
        anchors.topMargin: 10
        anchors.right: parent.right
        anchors.leftMargin: 20
        heightPadding: 5
        anchors.left: parent.left
        anchors.top: viewTicketButton.bottom
        anchors.rightMargin: 20
        onClicked: {
            viewTicketsForPunterClicked();
        }
    }

    Button {
        id: viewLastSoldTicketsButton
        x: 7
        y: 5
        text: "View recently sold tickets"
        anchors.topMargin: 10
        anchors.right: parent.right
        anchors.leftMargin: 20
        heightPadding: 5
        anchors.left: parent.left
        anchors.top: viewTicketsForPunterButton.bottom
        anchors.rightMargin: 20
        onClicked: {
            viewLastSoldTicketsClicked();
        }
    }
}
