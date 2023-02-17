
<!-- Inicialização do Owl Carousel -->

  $('.owl-carousel').owlCarousel({
     autoplay:false,
    loop: true, // Loop infinito
    margin: 10, // Margem entre itens
    nav: true, // Exibe botões de navegação
    navText: ["<i class='fas fa-chevron-left'></i>", "<i class='fas fa-chevron-right'></i>"], // Seta para navegação
    responsive: {
      0: {
        items: 1
      },
      600: {
        items: 3
      },
      1000: {
        items: 4
      }
    }
  });
