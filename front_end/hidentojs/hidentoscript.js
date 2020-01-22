$(function() {
   $("#edit_crush_deleteButton").click(function(){
      if (confirm("Deleting the crush will break any stable or unstable match made with this crush.\n\n Are you sure you want to delete?")){
         $('form#edit_crush_deleteForm').submit();
      } else{
      event.preventDefault();
      }
   });
});