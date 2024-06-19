import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { ActivatedRoute, Router, RouterOutlet } from '@angular/router';
import { footyService } from '../service/footyService.service';
import { CommonModule } from '@angular/common';
import {MatMenuModule} from '@angular/material/menu';
import {MatButtonModule} from '@angular/material/button';
import {MatGridListModule} from '@angular/material/grid-list';
import { Subscription } from 'rxjs';
import {MatCardModule} from '@angular/material/card';
import { DatePipe } from '@angular/common';
import {
  MAT_DIALOG_DATA,
  MatDialog,
  MatDialogActions,
  MatDialogClose,
  MatDialogContent,
  MatDialogRef,
  MatDialogTitle,
} from '@angular/material/dialog';
import { DialogComponent } from '../stats/dialogComponent.component';
import { SquadDialogComponent } from '../squad/squadDialogComponent.component';


@Component({
  selector: 'campeonato-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet, 
    MatButtonModule, 
    MatMenuModule,
    MatGridListModule, 
    MatCardModule, 
    DatePipe
  ],
  templateUrl: './campeonato.component.html',
  styleUrl: './campeonato.component.scss'
})
export class CampeonatoComponent {

  
  readonly dialog = inject(MatDialog);

  id_campeonato: string | null = null;
  dados?: any[];
  rodadaShow?: any;
  private routeSub!: Subscription;
  id_rodada = 0;
  
  constructor(private footyService: footyService, private route: ActivatedRoute, private router: Router) 
  {
    this.ngInit();
  }

  ngInit(): void
  { 
    this.routeSub = this.route.params.subscribe(params => {
      
      console.log("params", params);
      this.id_campeonato = params['id_campeonato'];
      this.id_rodada = 0;
      this.load();
    });
  }

  load()
  {
   
    this.footyService.obterRodadasCampeonato(this.id_campeonato).subscribe(
      (response) => {
        
        // this.id_rodada = 0;
        this.dados = response.rodadas;
        this.carregaRodada(0);
      },
      (error) => {
        console.error('Erro na requisição:', error);
      }
      );
  }

  ngOnDestroy(): void {
    
    if (this.routeSub) {
      this.routeSub.unsubscribe();
    }
  }

  carregaRodada(item: any)
  {
    this.id_rodada = this.id_rodada + item;
    console.log("rodada: ", this.id_rodada);

    if(this.dados != null){
      this.dados.forEach(e => {
          if(this.id_rodada == 0)
          {
            if(e.rodadaAtual != false)
            {
              this.id_rodada = e.rodada;
              this.rodadaShow = e;
            }
          }
          else if(this.id_rodada == e.rodada)
          {
              this.rodadaShow = e;
          }
      });
    }
  }
  OpenStats(item: any){
   
    console.log("item:", item);
    console.log(item.partida.mandante.id);
    console.log(item.partida.visitante.id);

    const dialogRef = this.dialog.open(DialogComponent, {
      width: '980px',
      height: '600px',
      maxHeight: '90vh',
      maxWidth: '90vw',
      data: {id_time_a: item.partida.mandante.id, id_time_b: item.partida.visitante.id, id_campeonato: this.id_campeonato}
    });

    dialogRef.afterClosed().subscribe(result => {
      this.load();
      // console.log('The dialog was closed');
      if (result !== undefined) {
        // this.animal.set(result);
      }
    });

    // var navigateTo = 'partida/';
    // navigateTo += this.id_campeonato + '/' + item.partida.mandante.id + '/' + item.partida.visitante.id;
    // console.log(navigateTo);
    // this.router.navigate([navigateTo]);
  }
  OpenSquad(item: any){
   
    // console.log("item:", item);
    // console.log(item.partida.id);
    // console.log(item.partida.visitante.id);

    const dialogRef = this.dialog.open(SquadDialogComponent, {
      width: '980px',
      height: '600px',
      maxHeight: '90vh',
      maxWidth: '90vw',
      data: {id_partida: item.partida.id}
    });

    dialogRef.afterClosed().subscribe(result => {
      // console.log('The dialog was closed');
      this.load();
      if (result !== undefined) {
        // this.animal.set(result);
      }
    });
    // var navigateTo = 'partida/';
    // navigateTo += this.id_campeonato + '/' + item.partida.mandante.id + '/' + item.partida.visitante.id;
    // console.log(navigateTo);
    // this.router.navigate([navigateTo]);
  }
}
