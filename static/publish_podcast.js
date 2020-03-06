
// change publish status between True or False
// const btns = $('.publish-form');
// btns.on('submit', (evt) => {
//   evt.preventDefault();
  
//   const podId = evt.target.id;
 
//   const text = $(`#submit-${evt.target.id}`).html();
//   let formInput = $(evt.target).serialize() // creates a dictionary with name:value (htm)
//   formInput.pod = podId

//   $.post(`/publish/${podId}`, formInput, (res) => {
//     console.log(res);
//     console.log($(`#submit-${evt.target.id}`))
//     if (text === "Publish") { 


//       $(`#submit-${evt.target.id}`).html("Published"); 
//     }

//     if (text === "Published") {

//       $(`#submit-${evt.target.id}`).html("Publish");
//     }
//   });
  
// });


const btns = $('.publish-btn');
    btns.on('click', (evt) => {
      evt.preventDefault();

      const audioId = $(evt.target).attr("id");

      const text = $(evt.target).html();
      
      let action = "published";
      console.log(text);
      if(text === "Published") {
        console.log("it was published")
        action = "Publish";
      }
      else{
        console.log("it wasn't published");
      }

      $.post("/publish", {publish: audioId, action: action}, (res) =>{
        console.log(res);

        if (res.status === "published") {    

          $(evt.target).html("Published"); 
        }
        if (res.status === "unpublished") {
          $(evt.target).html("Publish");
        }
      });      
    });