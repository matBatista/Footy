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
    public class CampeonatoController : ControllerBase
    {
        private readonly IConfiguration _configuration;

        private readonly IFootService _footService;
        public CampeonatoController(IConfiguration configuration, IFootService footService)
        {
            _configuration = configuration;
            _footService = footService; 
        }
        
        [HttpGet]
        public async Task<ActionResult> Get()
        {
            ObjectCampeonato camp = await _footService.RetornaCampeonatos();

            return Ok(camp);
        }

        [HttpGet]
        [Route("{id_campeonato}/rodadas")]
        public async Task<ActionResult> GetRodadas(int id_campeonato)
        {
            ObjectRodadas rodadas = await _footService.RetornaRodadasCampeonato(id_campeonato);

            return Ok(rodadas);
        }

        [HttpGet]
        [Route("{id_campeonato}/rodada")]
        public async Task<ActionResult> GetRodada(int id_campeonato, int id_rodada)
        {
            ObjectRodadas rodadas = await _footService.RetornaRodadasCampeonato(id_campeonato);

            Rodada rodada = rodadas.rodadas.Where(x => x.rodada == id_rodada).FirstOrDefault();

            return Ok(rodada);
        }

        [HttpGet]
        [Route("{id_campeonato}/ranking")]
        public async Task<ActionResult> GetRanking(int id_campeonato)
        {
            var list = await _footService.RetornaRankingFundamentos(id_campeonato);

            return Ok(list);
        }
        
        [HttpGet]
        [Route("/escalacao_partida")]
        public async Task<ActionResult> RetornaEscalacao(int id_partida)
        {
            var list = await _footService.RetornaEscalacao(id_partida);

            return Ok(list);
        }

    }
}
