$(function() {
   $("#edit_crush_deleteButton").click(function(){
      if (confirm("Deleting the crush will break any stable or unstable match made with this crush.\n\n Are you sure you want to delete?")){
         $('form#edit_crush_deleteForm').submit();
      } else{
      event.preventDefault();
      }
   });
});

$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();
});

$(document).ready(function() {
   $("#instagramVerify").click(function(){
      var instagramUsername = $("#id_crushUsername").val();
      if (!instagramUsername.trim() || instagramUsername.length == 0){
        alert("Enter an Instagram username to verify.");
      } else if (hasWhiteSpace(instagramUsername.trim())){
        alert("Instagram username should not contain spaces.")
      } else if (hasatsymbol(instagramUsername.trim())){
        alert("Do not include '@' in Instagram username.")
      } else{
        instagramLink = "https://www.instagram.com/" + instagramUsername.trim();
        window.open(instagramLink, '_blank')
      }
   });
});

function hasatsymbol(s) {
  return s.indexOf('@') >= 0;
}

function hasWhiteSpace(s) {
  return s.indexOf(' ') >= 0;
}

$(function()
{
  $("#hidentoform").submit(function(){
    $("input[type='submit']", this)
      .val("Please Wait...")
      .attr("disabled", true);
    return true;
  });
});

$(".edit_crush_activeClass").change(function() {
    if(!this.checked && this.defaultChecked) {
        alert("You are about to deactivate this crush.\n\n Deactivating will break any stable or unstable match made with this crush.")
    }
});
