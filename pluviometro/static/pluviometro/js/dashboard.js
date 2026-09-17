document.addEventListener(
    "DOMContentLoaded",
    function () {

        const botaoCalcular =
            document.getElementById(
                "btn-calcular-periodo"
            );

        if (botaoCalcular) {

            botaoCalcular.addEventListener(
                "click",
                calcularVolumePeriodo
            );
        }


        const periodoGrafico =
            document.getElementById(
                "periodo-grafico"
            );

        if (periodoGrafico) {

            periodoGrafico.addEventListener(
                "change",
                carregarGrafico
            );
        }


        carregarDashboard();

        carregarGrafico();


        // Atualização automática
        setInterval(
            carregarDashboard,
            30000
        );

        setInterval(
            carregarGrafico,
            30000
        );
    }
);


// ==================================================
// CONFIGURAÇÕES
// ==================================================

const API_BASE =
    "/pluviometro/api/leituras/";

const DISPOSITIVO_PADRAO =
    "PLUVIO-001";

let graficoChuva = null;


// ==================================================
// DASHBOARD
// ==================================================

async function carregarDashboard() {

    const selectDispositivo =
        document.getElementById(
            "select-dispositivo"
        );

    const dispositivo =
        selectDispositivo?.value ||
        DISPOSITIVO_PADRAO;


    const url =
        API_BASE +
        "resumo/?dispositivo=" +
        encodeURIComponent(
            dispositivo
        );


    try {

        const resposta =
            await fetch(url);


        if (!resposta.ok) {

            throw new Error(
                "Erro HTTP: " +
                resposta.status
            );
        }


        const dados =
            await resposta.json();


        atualizarElemento(
            "dispositivo",
            dados.dispositivo ||
            dispositivo
        );


        atualizarElemento(
            "chuva-hoje",
            formatarMm(
                dados.chuva_hoje
            )
        );


        atualizarElemento(
            "chuva-hora",
            formatarMm(
                dados.chuva_ultima_hora
            )
        );


        atualizarElemento(
            "chuva-mes",
            formatarMm(
                dados.chuva_mes
            )
        );


        atualizarElemento(
            "chuva-total",
            formatarMm(
                dados.chuva_total
            )
        );


        atualizarElemento(
            "ultima-leitura",
            dados.ultima_leitura ||
            "--"
        );


        atualizarElemento(
            "pulsos",
            dados.pulsos ??
            "--"
        );


    } catch (erro) {

        console.error(
            "Erro ao carregar dashboard:",
            erro
        );
    }
}


// ==================================================
// GRÁFICO
// ==================================================

async function carregarGrafico() {

    const canvas =
        document.getElementById(
            "grafico-chuva"
        );

    if (!canvas) {
        return;
    }


    const selectDispositivo =
        document.getElementById(
            "select-dispositivo"
        );

    const dispositivo =
        selectDispositivo?.value ||
        DISPOSITIVO_PADRAO;


    const selectPeriodo =
        document.getElementById(
            "periodo-grafico"
        );

    const periodo =
        selectPeriodo?.value ||
        "24h";


    const loading =
        document.getElementById(
            "grafico-loading"
        );

    const erro =
        document.getElementById(
            "grafico-erro"
        );


    loading?.classList.remove(
        "d-none"
    );

    erro?.classList.add(
        "d-none"
    );


    try {

        const parametros =
            new URLSearchParams({
                dispositivo: dispositivo,
                periodo: periodo
            });


        const url =
            API_BASE +
            "grafico/?" +
            parametros.toString();


        console.log(
            "Carregando gráfico:",
            url
        );


        const resposta =
            await fetch(url);


        if (!resposta.ok) {

            throw new Error(
                "Erro HTTP: " +
                resposta.status
            );
        }


        const dados =
            await resposta.json();


        console.log(
            "Dados do gráfico:",
            dados
        );


        criarGrafico(
            canvas,
            dados
        );


    } catch (error) {

        console.error(
            "Erro ao carregar gráfico:",
            error
        );


        if (erro) {

            erro.textContent =
                error.message ||
                "Não foi possível carregar o gráfico.";

            erro.classList.remove(
                "d-none"
            );
        }


    } finally {

        loading?.classList.add(
            "d-none"
        );
    }
}


// ==================================================
// CRIAR GRÁFICO CHART.JS
// ==================================================

function criarGrafico(
    canvas,
    dados
) {

    const labels =
        dados.dados.map(
            item => item.periodo
        );


    const valores =
        dados.dados.map(
            item => Number(
                item.chuva_mm
            )
        );


    // Destrói gráfico anterior
    if (graficoChuva) {

        graficoChuva.destroy();

        graficoChuva = null;
    }


    graficoChuva =
        new Chart(
            canvas,
            {
                type: "bar",

                data: {

                    labels: labels,

                    datasets: [
                        {
                            label:
                                "Precipitação (mm)",

                            data: valores,

                            borderWidth: 1,

                            borderRadius: 5
                        }
                    ]
                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    interaction: {
                        mode: "index",
                        intersect: false
                    },

                    plugins: {

                        legend: {
                            display: false
                        },

                        tooltip: {

                            callbacks: {

                                label:
                                    function (
                                        context
                                    ) {

                                        return (
                                            " " +
                                            Number(
                                                context.raw
                                            ).toFixed(3) +
                                            " mm"
                                        );
                                    }
                            }
                        }
                    },

                    scales: {

                        x: {

                            title: {
                                display: true,
                                text: "Período"
                            }
                        },

                        y: {

                            beginAtZero: true,

                            title: {
                                display: true,
                                text: "Precipitação (mm)"
                            },

                            ticks: {

                                callback:
                                    function (
                                        value
                                    ) {

                                        return (
                                            value +
                                            " mm"
                                        );
                                    }
                            }
                        }
                    }
                }
            }
        );
}


// ==================================================
// CALCULAR VOLUME POR PERÍODO
// ==================================================

async function calcularVolumePeriodo() {

    const dispositivoElement =
        document.getElementById(
            "select-dispositivo"
        );

    const inicioElement =
        document.getElementById(
            "periodo-inicio"
        );

    const fimElement =
        document.getElementById(
            "periodo-fim"
        );

    const botao =
        document.getElementById(
            "btn-calcular-periodo"
        );

    const resultado =
        document.getElementById(
            "resultado-periodo"
        );

    const erro =
        document.getElementById(
            "erro-periodo"
        );

    const volume =
        document.getElementById(
            "volume-periodo"
        );


    if (
        !dispositivoElement ||
        !inicioElement ||
        !fimElement ||
        !resultado ||
        !erro ||
        !volume
    ) {

        console.error(
            "Elementos do cálculo por período não encontrados."
        );

        return;
    }


    const dispositivo =
        dispositivoElement.value ||
        DISPOSITIVO_PADRAO;

    const inicio =
        inicioElement.value;

    const fim =
        fimElement.value;


    erro.classList.add(
        "d-none"
    );

    resultado.classList.add(
        "d-none"
    );


    if (!inicio || !fim) {

        mostrarErro(
            erro,
            "Informe a data e hora inicial e final."
        );

        return;
    }


    if (inicio >= fim) {

        mostrarErro(
            erro,
            "A data inicial deve ser anterior à data final."
        );

        return;
    }


    const textoOriginal =
        botao.innerHTML;


    botao.disabled = true;

    botao.innerHTML = `
        <span
            class="spinner-border spinner-border-sm me-1"
            role="status"
        ></span>
        Calculando...
    `;


    try {

        const parametros =
            new URLSearchParams({
                dispositivo: dispositivo,
                inicio: inicio,
                fim: fim
            });


        const resposta =
            await fetch(
                API_BASE +
                "periodo/?" +
                parametros.toString()
            );


        const dados =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                dados.erro ||
                "Erro ao calcular o período."
            );
        }


        volume.textContent =
            formatarMm(
                dados.chuva_mm
            );


        resultado.classList.remove(
            "d-none"
        );


    } catch (error) {

        console.error(
            "Erro:",
            error
        );


        mostrarErro(
            erro,
            error.message ||
            "Não foi possível calcular o volume."
        );


    } finally {

        botao.disabled = false;

        botao.innerHTML =
            textoOriginal;
    }
}


// ==================================================
// FUNÇÕES AUXILIARES
// ==================================================

function atualizarElemento(
    id,
    valor
) {

    const elemento =
        document.getElementById(id);

    if (elemento) {

        elemento.textContent =
            valor;
    }
}


function formatarMm(
    valor
) {

    if (
        valor === null ||
        valor === undefined ||
        valor === ""
    ) {

        return "--";
    }


    const numero =
        Number(valor);


    if (isNaN(numero)) {

        return "--";
    }


    return (
        numero.toFixed(3) +
        " mm"
    );
}


function mostrarErro(
    elemento,
    mensagem
) {

    elemento.textContent =
        mensagem;

    elemento.classList.remove(
        "d-none"
    );
}