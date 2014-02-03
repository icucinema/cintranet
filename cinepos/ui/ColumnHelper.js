var columns = {}

function calcColumnWidths(model, parent)
{
    for (var i = 0; i < model.count; ++i)
    {
        var data = model.get(i)
        for (var key in data)
        {
            if (!columns[key]) {
                columns[key] = 0
            }

            var textElement = Qt.createQmlObject(
                    'import Qt 4.7;'
                    + 'Text {'
                    + '   text: "' + data[key] + '" '
                    + '}',
                    parent, "calcColumnWidths")

            columns[key] = Math.max(textElement.width, columns[key])
            textElement.destroy()
        }
    }
    return columns
}
