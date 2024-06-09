using Microsoft.AspNetCore.JsonPatch.Internal;
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
    public class FundamentoController : ControllerBase
    {
        private readonly IConfiguration _configuration;
        private readonly IFootService _footService;
        public FundamentoController(IConfiguration configuration, IFootService footService)
        {
            _configuration = configuration;
            _footService = footService; 
        }

        [HttpGet]
        [Route("/fundamento")]
        public async Task<ActionResult> getRankingFundamento(int id_campeonato, int id_fundamento)
        {
            ObjectFundamentoJogador list = await _footService.RetornaFundamentoJogador(id_campeonato, id_fundamento);

            return Ok(list);
        }
        [HttpGet]
        [Route("/fundamentojogador")]
        public async Task<ActionResult> getFundamentoJogador(int id_campeonato, int id_fundamento, int id_jogador)
        {
            ObjectFundamentoJogador list = await _footService.RetornaFundamentoJogador(id_campeonato, id_fundamento);

            var jogador = list.fundamentos.FirstOrDefault(x => x.idJogador == id_jogador);

            return Ok(jogador);
        }
        [HttpGet]
        [Route("/fundamentotime")]
        public async Task<ActionResult> getFundamentoTime(int id_campeonato, int id_fundamento, int id_time)
        {
            ObjectFundamentoJogador list = await _footService.RetornaFundamentoJogador(id_campeonato, id_fundamento);
            
            var time = list.fundamentos.Where(e => e.idTeam == id_time);

            return Ok(time);
        }

    }
}
