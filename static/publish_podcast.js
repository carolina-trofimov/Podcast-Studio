
const btns = $('.publish-btn');
    btns.on('click', (evt) => {
      evt.preventDefault();

      const audioId = $(evt.target).attr("id");

      const text = $(evt.target).html();
      
      let action;

      if(text === "Unpublish") {
        action = "unpublish";
      }
      else{
       action = "publish";
      }

      $.post("/publish", {publish: audioId, action: action}, (res) =>{
        console.log(res);

        if (res.status === "published") {    
          $(evt.target).html("Unpublish"); 
        }
        if (res.status === "unpublished") {
          $(evt.target).html("Publish");
        }
      });      
    });