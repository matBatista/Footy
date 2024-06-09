using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Models;
using Models.Model;
using Newtonsoft.Json;
using Services.Interfaces;
using System.Net.Http.Headers;

namespace FootAnalises.Controllers
{

    [ApiController]
    [Route("[controller]")]
    public class EquipeController : ControllerBase
    {
        private readonly IConfiguration _configuration;
        private readonly IFootService _footService;
        public EquipeController(IConfiguration configuration, IFootService footService)
        {
            _configuration = configuration;
            _footService = footService; 
        }

        //http://localhost:5169/equipe?id_campeonato=984&id_equipe=1004
        [HttpGet]
        [Route("/equipe")]
        public async Task<ActionResult> GetEquipeCampeonato(int id_campeonato, int id_equipe)
        {
            ObjectFundamentoGeral list = await _footService.RetornaRankingFundamentos(id_campeonato);

            // Encontrar o EquipeDetalhe correspondente ao Id
            var equipeDetalhe = list.pros.SelectMany(f => f.equipes).FirstOrDefault(e => e.id == id_equipe)
                                ?? list.contra.SelectMany(f => f.equipes).FirstOrDefault(e => e.id == id_equipe);

            // Criar a instância de EquipeDetalhada
            EquipeDetalhada equipeDetalhada = new EquipeDetalhada(equipeDetalhe);

            equipeDetalhada.FundamentosPros = AdicionarFundamentos(list.pros, id_equipe);

            equipeDetalhada.FundamentosContra = AdicionarFundamentos(list.contra, id_equipe);

            return Ok(equipeDetalhada);
        }
        //http://localhost:5169/equipe?id_campeonato=984&id_equipe=1004
        [HttpGet]
        [Route("/jogador")]
        public async Task<ActionResult> GetJogador(int id_campeonato, int id_fundamento)
        {
            var list = await _footService.RetornaFundamentoJogador(id_campeonato, id_fundamento);

            return Ok(list);
        }
        public List<FundamentoEquipe> AdicionarFundamentos(List<FundamentosGeral> fundamentos, int id_equipe)
        {
            List<FundamentoEquipe> listFundamento = new List<FundamentoEquipe>();
            
            foreach(var fundamento in fundamentos)
            {
                var detalhe = fundamento.equipes.FirstOrDefault(x => x.id == id_equipe);
                
                if(detalhe != null)
                {
                    FundamentoEquipe fEquipe = new FundamentoEquipe
                    {
                        certos = detalhe.certos,
                        errados = detalhe.errados,
                        totais = detalhe.totais,
                        id = fundamento.id,
                        nome = fundamento.nome
                    };

                    listFundamento.Add(fEquipe);
                }
            }

            return listFundamento;
        }

    }
}
