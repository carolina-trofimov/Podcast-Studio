
// change publish status between True or False
const btns = $('.publish-form');
btns.on('submit', (evt) => {
  evt.preventDefault();
  
  const podId = evt.target.id;
 
  const text = $(`#submit-${evt.target.id}`).html();
  let formInput = $(evt.target).serialize() // creates a dictionary with name:value (htm)
  formInput.pod = podId

  $.post(`/publish/${podId}`, formInput, (res) => {
    console.log(res);
    console.log($(`#submit-${evt.target.id}`))
    if (text === "Publish") { 


      $(`#submit-${evt.target.id}`).html("Published"); 
    }

    if (text === "Published") {

      $(`#submit-${evt.target.id}`).html("Publish");
    }
  });
  
});
