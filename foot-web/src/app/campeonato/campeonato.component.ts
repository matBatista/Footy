import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { footyService } from '../service/footyService.service';

@Component({
  selector: 'campeonato-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './campeonato.component.html',
  styleUrl: './campeonato.component.scss'
})
export class CampeonatoComponent {

  title = 'Lista de Campeonatos';

  dados?: any[];

  constructor(private footyService: footyService) {
    this.footyService.obterCampeonatos().subscribe(
      (response) => {
        console.log(response);
        this.dados = response;
      },
      (error) => {
        console.error('Erro na requisição:', error);
      }
    );
  }
}
