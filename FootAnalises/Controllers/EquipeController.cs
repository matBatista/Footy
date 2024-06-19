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

            //equipeDetalhada.FundamentosPros = AdicionarFundamentos(list.pros, id_equipe);

            //equipeDetalhada.FundamentosContra = AdicionarFundamentos(list.contra, id_equipe);

            return Ok(equipeDetalhada);
        }

        [HttpGet]
        [Route("/equipe_fundamento")]
        public async Task<ActionResult> GetFundamentosEquipe(int id_campeonato, int id_equipe)
        {
            List<FundamentoStats> list = await _footService.RetornaFundamentosEquipe(id_campeonato, id_equipe);
            return Ok(list);
        }
       
        //http://localhost:5169/equipe?id_campeonato=984&id_equipe=1004
        [HttpGet]
        [Route("/jogador")]
        public async Task<ActionResult> GetJogador(int id_campeonato, int id_fundamento)
        {
            var list = await _footService.RetornaFundamentoJogador(id_campeonato, id_fundamento);

            return Ok(list);
        }
      



    }
}

