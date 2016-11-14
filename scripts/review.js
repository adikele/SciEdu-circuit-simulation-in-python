/* This function checks the options selected by user in assingments and background */
$(document).ready(function(){
    //Hide submission result boxes
    $(".success").hide();
    $(".failure").hide();

    $("button").click(function(){
        //By default the submission is correct, it may be changed to incorrect if the is a mistake
        $(".result").css("background-color", "#AAFFAA");
        $(".result").text( "Correct! You can now move on to the next exercise!" );
        
	//Mark all answers correct
	$(".success").show();
	$(".failure").hide();
	//Select all checked options
        $('input[name=option]').each(function () {        
                $(this).parent().css("background-color", "#AAFFAA");
                //alert("Correct answer!");
        });	

	//Check for mistakes
        $('input[name=option]:not(:checked)').each(function () { 
            if (this.value == "correct") {
                $(this).parent().css("background-color", "#FF704D");
		$(".success").hide();
    		$(".failure").show();
            }
        });
    });
});

/* Old incorrect implementation*/
/*
$(document).ready(function(){
    $("button").click(function(){
        //By default the submission is correct, it may be changed to incorrect if the is a mistake
        $(".result").css("background-color", "#AAFFAA");
        $(".result").text( "Correct! You can move to the next exercise!" );

        //Select all checked options
        $('input[name=option]:checked').each(function () {
            if (this.value == "incorrect") {
                $(this).parent().css("background-color", "#FF704D");
                //alert("Incorrect answer!");
                $(".result").css("background-color", "#FF704D");
                $(".result").text( "Incorrect! Please correct your mistakes!" );
            }
            else {
                $(this).parent().css("background-color", "#AAFFAA");
                //alert("Correct answer!");
            }
        });
    });
});
*/
