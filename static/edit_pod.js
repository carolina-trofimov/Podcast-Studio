

$(document).ready(function() {
    $('#"{{ audio.audio_id }}"').load('static/my_raw_podcast.html');
    return $('#"{{ audio.audio_id }}"').attr("id")
});

