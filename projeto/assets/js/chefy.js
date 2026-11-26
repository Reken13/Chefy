/*
 * chefy.js — comportamento no browser, com jQuery.
 * jQuery: $('seletor') escolhe elementos da página; .on('evento', função) reage a ações.
 */
$(function () {

    // 1) Pedir confirmação antes de apagar:
    //    <form data-confirmar="Apagar este item?"> ... </form>
    $('form[data-confirmar]').on('submit', function (evento) {
        if (!window.confirm($(this).data('confirmar'))) {
            evento.preventDefault();   // cancela o envio do formulário
        }
    });

    // 2) Filtros que se aplicam sozinhos ao mudar:
    //    <select data-auto-enviar> / <input type="checkbox" data-auto-enviar>
    $('[data-auto-enviar]').on('change', function () {
        $(this).closest('form').trigger('submit');
    });

    // 3) Formulário de receitas: adicionar e remover linhas de ingredientes.
    var $lista = $('#lista-ingredientes');
    if ($lista.length) {
        // Copia o molde escondido (<template>) e junta-o à lista.
        $('#adicionar-ingrediente').on('click', function () {
            $lista.append($('#molde-ingrediente').html());
        });

        // Os botões "remover" são criados dinamicamente, por isso o evento
        // fica na lista e filtra pelo botão (delegação de eventos).
        $lista.on('click', '.remover-ingrediente', function () {
            if ($lista.children('.linha-ingrediente').length > 1) {
                $(this).closest('.linha-ingrediente').remove();
            } else {
                // Última linha: em vez de a apagar, limpa-a.
                $(this).closest('.linha-ingrediente').find('select').val('').end().find('input').val('');
            }
        });
    }
});
