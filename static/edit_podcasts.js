
$(".podcast-name").on("dblclick", function(evt) {
    evt.preventDefault();
    const nameToChange = $(evt.target);
    const data = nameToChange.data();
    nameToChange.html(`<input class='podcast-name-input' type="text" data-pod-id=${data.podId} value=${nameToChange.text()}/>`)
});

$('#podcast-list').on('keypress', function(evt) {
    console.log("we are inside the keydown", evt.keyCode)
    if (evt.keyCode === 13) {
        const target = $(evt.target);
        const data = target.data();
        const newName = target.val();
        const podId = data.podId;
        $.ajax({
          type: "POST",
          url: `/audio/${podId}`,
          data: {name : newName},
          success: function () {
            // Change the target back to div
            target.parent().html(newName)
          }
        });
        
        
    }
})