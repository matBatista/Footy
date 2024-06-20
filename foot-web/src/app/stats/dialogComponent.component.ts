import { Component, inject, model } from '@angular/core';
import { ActivatedRoute, Router, RouterOutlet } from '@angular/router';
import { footyService } from '../service/footyService.service';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { Subscription } from 'rxjs';
import { DatePipe } from '@angular/common';
import {MatTableModule} from '@angular/material/table';
import {
  MAT_DIALOG_DATA,
  MatDialog,
  MatDialogActions,
  MatDialogClose,
  MatDialogContent,
  MatDialogRef,
  MatDialogTitle,
} from '@angular/material/dialog';
import {MatGridListModule} from '@angular/material/grid-list';
import { DialogData } from '../interfaces/DialogData';
import { Fundamentos } from '../interfaces/Fundamentos';
import { Estatisticas } from '../interfaces/Estatisticas';

@Component({
  selector: 'dialogComponent',
  templateUrl: './dialogComponent.component.html',
  styleUrl: './dialogComponent.component.scss',
  standalone: true,
  imports: [
    CommonModule, 
    RouterOutlet, 
    MatButtonModule, 
    DatePipe, 
    MatTableModule, 
    MatButtonModule,
    MatDialogTitle,
    MatDialogContent,
    MatDialogActions,
    MatDialogClose,
    MatGridListModule
  ],
 
})


export class DialogComponent {
  readonly dialogRef = inject(MatDialogRef<DialogComponent>);
  readonly data = inject<DialogData>(MAT_DIALOG_DATA);
  
  // readonly dados = model(this.data.id_time_a);

  id_campeonato: number | null = null;
  id_equipe_a: number | null = null;
  id_equipe_b: number | null = null;
  clickedRows = new Set<Fundamentos>();
  
  dados_pros?: any[];
  dados_cons?: any[];
  
  fundamento_equipe_a?: Fundamentos[] = [];
  fundamento_equipe_b?: Fundamentos[] = [];
  
  estatisticas: Estatisticas[] = [];

  private routeSub!: Subscription;
  displayedColumns: string[] = ['nome','qtdJogos','pros_certos','pros_errados','pros_media','pros_total','cons_certos','cons_errados','cons_media','cons_total'];

  constructor(private footyService: footyService, private route: ActivatedRoute, private router: Router) 
  {
   
  }

  ngOnInit(): void
  { 
   
    this.id_campeonato = this.data.id_campeonato;
    this.id_equipe_a = this.data.item.mandante.id;
    this.id_equipe_b = this.data.item.visitante.id;
    
    this.load();

    // let stats: Estatisticas = {
    //     mandante = {
    //       nome: this.fundamento_equipe_a.
    //     }
    // }
 
  }

  async load(){

    await this.footyService.obterListaFundamentos(this.id_campeonato,this.id_equipe_a).subscribe(
      (response) => {
        
        this.fundamento_equipe_a = response;
       
      },
      (error) => {
        console.error('Erro na requisição:', error);
      }
    );

    await this.footyService.obterListaFundamentos(this.id_campeonato,this.id_equipe_b).subscribe(
      (response) => {
        
        this.fundamento_equipe_b = response;
       
      },
      (error) => {
        console.error('Erro na requisição:', error);
      }
    );

    console.log("fundamentos_a", this.fundamento_equipe_a);
    console.log("fundamentos_b", this.fundamento_equipe_b);

  }

  ngOnDestroy(): void {
    
    if (this.routeSub) {
      this.routeSub.unsubscribe();
    }
  }

  
}
