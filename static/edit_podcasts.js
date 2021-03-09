$(document).ready(function() {
  
  const returnKey = 13 //key Enter

  $(".podcast-name").on("dblclick", function(evt) {
      const nameToChange = $(evt.target);
      const data = nameToChange.data();
      nameToChange.html(`<input class='podcast-name-input' type="text" data-podcast-id=${data.podcastId} value=${nameToChange.text()}/>`)
  });
  
  $('#podcast-list').on('keypress', function(evt) {
      if (evt.keyCode === returnKey) {
          const target = $(evt.target);
          const data = target.data();
          const newName = target.val();
          const podcastId = data.podcastId;
          
          $.ajax({
            type: "POST",
            url: `/audio/${podcastId}`,
            data: {name : newName},
            success: function () {
              // Change the target back to div
              target.parent().html(newName)
            }
          });
          
      }
  })
})

