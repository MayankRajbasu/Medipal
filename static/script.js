$('.slider').owlCarousel({
    loop: true,            
    nav: false,
    autoplay: true,
    autoplayTimeout: 5000,
    smartSpeed: 450,
    margin: 20,
    responsive: {
        0: {
            items: 1
        },
        768: {
            items: 2
        },
        991: {
            items: 3
        },
        1200: {
            items: 3
        },
        1440: {
         items: 4
        },
        1920: {
            items: 4
        }
    }
});

$(window).scroll(function(){
    $('.primary-header').toggleClass('scrolled',$(this).scrollTop()>80);
});


function deleteParagraph() {
    var paragraph = document.getElementById("error");
    paragraph.remove();   
};