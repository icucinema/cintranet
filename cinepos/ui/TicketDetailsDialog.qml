import QtQuick 2.0

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

    signal voidTicket(string ticketId);
    signal refundTicket(string ticketId);
    signal reprintTicket(string ticketId);

    property var ticketDetails: ({
                                     id: "",
                                     status: "",
                                     ticket_type: {
                                         name: "",
                                         event: {
                                             name: "",
                                             start_time: 0
                                         }
                                     },
                                     punter: false,
                                     entitlement: false
                                 });

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
        text: qsTr("Ticket Details")
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

    Grid {
        id: grid1
        height: 216
        anchors.right: parent.right
        anchors.rightMargin: 20
        anchors.left: parent.left
        anchors.leftMargin: 20
        anchors.top: parent.top
        anchors.topMargin: 56
        spacing: 10
        columns: 2

        Text {
            renderType: Text.NativeRendering
            id: ticketNumberLabel
            text: qsTr("Ticket Number: ")
            font.bold: true
            font.pixelSize: 16
        }

        Text {
            renderType: Text.NativeRendering
            id: ticketNumberInfo
            height: 20
            text: ticketDetails.id
            font.pixelSize: 16
            wrapMode: Text.WordWrap
        }

        Text {
            renderType: Text.NativeRendering
            id: ticketStatusLabel
            text: qsTr("Status: ")
            font.bold: true
            font.pixelSize: 16
        }

        Text {
            renderType: Text.NativeRendering
            id: ticketStatusInfo
            height: 20
            font.pixelSize: 16
            text: ticketDetails.status
            wrapMode: Text.WordWrap
        }

        Text {
            renderType: Text.NativeRendering
            id: ticketTypeLabel
            text: qsTr("Ticket Type: ")
            font.bold: true
            font.pixelSize: 16
        }

        Text {
            renderType: Text.NativeRendering
            id: ticketTypeInfo
            height: 20
            font.pixelSize: 16
            text: ticketDetails.ticket_type.name
            wrapMode: Text.WordWrap
        }

        Text {
            renderType: Text.NativeRendering
            id: eventNameLabel
            text: qsTr("Event Name: ")
            font.bold: true
            font.pixelSize: 16
        }

        Text {
            renderType: Text.NativeRendering
            id: eventNameInfo
            height: 20
            font.pixelSize: 16
            text: ticketDetails.ticket_type.event.name
            wrapMode: Text.WordWrap
            clip: true
        }

        Text {
            renderType: Text.NativeRendering
            id: eventDateLabel
            text: qsTr("Event Date: ")
            font.bold: true
            font.pixelSize: 16
        }

        Text {
            renderType: Text.NativeRendering
            id: eventDateInfo
            height: 20
            font.pixelSize: 16
            text: formatDate(ticketDetails.ticket_type.event.start_time) + " " + formatTime(ticketDetails.ticket_type.event.start_time)
            wrapMode: Text.WordWrap
        }

        Text {
            renderType: Text.NativeRendering
            id: punterNameLabel
            text: qsTr("Customer Name: ")
            font.bold: true
            font.pixelSize: 16
            visible: (!!ticketDetails.punter)
        }

        Text {
            renderType: Text.NativeRendering
            id: punterNameInfo
            height: 20
            font.pixelSize: 16
            text: (!!ticketDetails.punter) ? ticketDetails.punter.name : ""
            visible: (!!ticketDetails.punter)
            wrapMode: Text.WordWrap
            clip: true
        }

        Text {
            renderType: Text.NativeRendering
            id: entitlementNameLabel
            text: qsTr("Used Entitlement: ")
            font.bold: true
            font.pixelSize: 16
            visible: (!!ticketDetails.entitlement)
        }

        Text {
            renderType: Text.NativeRendering
            id: entitlementNameInfo
            height: 20
            font.pixelSize: 16
            text: (!!ticketDetails.entitlement) ? ticketDetails.entitlement.name : ""
            visible: (!!ticketDetails.entitlement)
            wrapMode: Text.WordWrap
            clip: true
        }

    }

    Button {
        id: voidButton
        x: 237
        text: "Void"
        anchors.top: parent.top
        anchors.topMargin: 17
        anchors.right: refundButton.left
        anchors.rightMargin: 20
        onClicked: voidTicket(ticketDetails.id.toString())
        visible: (ticketDetails.status === 'live')
    }

    Button {
        id: refundButton
        x: 308
        text: "Refund"
        anchors.top: parent.top
        anchors.topMargin: 17
        anchors.right: reprintButton.left
        anchors.rightMargin: 20
        onClicked: refundTicket(ticketDetails.id.toString())
        visible: (ticketDetails.status === 'live')
    }

    Button {
        id: reprintButton
        x: 308
        text: (ticketDetails.status === 'pending_collection' ? "Print" : "Reprint")
        anchors.top: parent.top
        anchors.topMargin: 17
        anchors.right: parent.right
        anchors.rightMargin: 20
        onClicked: reprintTicket(ticketDetails.id.toString())
    }
}
