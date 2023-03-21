
// Seleciona o elemento com a classe 'essencia-list' e aplica o plugin slick()
let slickList1 = $('.slick-list');
let slickList2 = $('.essencia-list2');

slickList1.slick({
  slidesToShow: 4,
  slidesToScroll: 1,
  arrows: true,
  infinite: true,
  autoplay: false,
  // Define a configuração do número de slides exibidos em diferentes tamanhos de tela
  responsive: [
    {
      breakpoint: 992,
      settings: {
        slidesToShow: 3
      }
    },
     {
      breakpoint: 776,
      settings: {
        slidesToShow: 2
      }
    },
    {
      breakpoint: 576,
      settings: {
        slidesToShow: 1
      }
    }
  ]
});

slickList2.slick({
 slidesToShow: 4,
  slidesToScroll: 1,
  arrows: true,
  infinite: true,
  autoplay: false,
  // Define a configuração do número de slides exibidos em diferentes tamanhos de tela
  responsive: [
    {
      breakpoint: 992,
      settings: {
        slidesToShow: 3
      }
    },
     {
      breakpoint: 776,
      settings: {
        slidesToShow: 2
      }
    },
    {
      breakpoint: 576,
      settings: {
        slidesToShow: 1
      }
    }
  ]
});

// Seleciona os elementos com a classe 'prev-btn' e 'next-btn' e adiciona um listener para as ações de clique, que chama os métodos do plugin slick()
let prevBtn = $('.prev-btn');
let nextBtn = $('.next-btn');

prevBtn.click(function() {
  slickList1.slick('slickPrev');
  slickList2.slick('slickPrev');
});

nextBtn.click(function() {
  slickList1.slick('slickNext');
  slickList2.slick('slickNext');
});

// Adiciona um listener para o evento 'afterChange' do plugin slick() que define a classe 'slick-disabled' nos botões 'prev-btn' e 'next-btn' com base na posição do slide atual
slickList1.on('afterChange', function(event, slick, currentSlide) {
  prevBtn.toggleClass('slick-disabled', currentSlide === 0);
  nextBtn.toggleClass('slick-disabled', currentSlide === slick.slideCount - 1);
});

slickList2.on('afterChange', function(event, slick, currentSlide) {
 prevBtn.toggleClass('slick-disabled', currentSlide === 0);
  nextBtn.toggleClass('slick-disabled', currentSlide === slick.slideCount - 1);
});
