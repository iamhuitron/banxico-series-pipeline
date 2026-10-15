"""
Command Line Interface for Banxico Series Pipeline.
"""

import sys
import argparse
from .extract import BanxicoExtractor
from .transform import MacroTransformer
from .load import MacroStorage
from .analytics import MacroAnalytics


def main():
    parser = argparse.ArgumentParser(
        description="Banxico Series Pipeline: Macroeconomic Time-Series ETL & Analytics"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Run ETL
    run_parser = subparsers.add_parser("run-etl", help="Ejecuta la pipeline de extracción, transformación y carga")
    run_parser.add_argument("--lake-dir", default="./data/macro_lake", help="Directorio raíz para Parquet y DuckDB")
    run_parser.add_argument("--use-offline-data", action="store_true", default=True, help="Usar dataset histórico offline")

    # Dashboard / Snapshot
    dash_parser = subparsers.add_parser("snapshot", help="Muestra el resumen macroeconómico más reciente")
    dash_parser.add_argument("--lake-dir", default="./data/macro_lake")

    # Stats
    stats_parser = subparsers.add_parser("stats", help="Calcula estadísticas descriptivas y correlaciones")
    stats_parser.add_argument("--lake-dir", default="./data/macro_lake")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    storage = MacroStorage(base_dir=args.lake_dir)
    analytics = MacroAnalytics(storage.con)

    if args.command == "run-etl":
        print("Iniciando extracción de series Banxico SIE...")
        extractor = BanxicoExtractor()
        raw_data = extractor.get_sample_historical_dataset()
        print(f"✓ Extraídas {sum(len(v) for v in raw_data.values())} observaciones en 4 series clave.")

        print("Transformando y armonizando frecuencias temporales...")
        indicators = MacroTransformer.align_and_harmonize_series(raw_data)
        print(f"✓ Generados {len(indicators)} registros temporales diarios armonizados.")

        saved_count = storage.save_indicators(indicators)
        print(f"✓ Persistidos {saved_count} días en DuckDB y particionados en Apache Parquet.")

    elif args.command == "snapshot":
        snap = analytics.get_latest_indicators()
        if not snap:
            print("No se encontraron registros. Ejecuta primero 'run-etl'.")
            sys.exit(1)
        print("\n======================= SNAPSHOT MACROECONÓMICO =======================")
        print(f"Fecha de Referencia : {snap['fecha']}")
        print(f"Tipo de Cambio FIX  : ${snap['usd_mxn_fix']:.4f} MXN/USD")
        print(f"Tasa TIIE (28 días) : {snap['tiie_28d']:.2f}%")
        print(f"Valor UDIS          : ${snap['udis']:.6f} MXN")
        print(f"Índice INPC         : {snap['inpc']:.2f} pts")
        print(f"Inflación Anual     : {snap['inflacion_anual']:.2f}%")
        print(f"Tasa de Interés Real: {snap['tasa_real']:.2f}% (TIIE - Inflación)")
        print("========================================================================\n")

    elif args.command == "stats":
        stats = analytics.get_summary_statistics()
        corr = analytics.get_correlation_matrix()
        print("\n===================== ESTADÍSTICAS Y CORRELACIONES =====================")
        print(f"Observaciones Analizadas : {stats['num_observaciones']}")
        print(f"USD/MXN Mínimo / Máximo : ${stats['usd_min']:.4f} / ${stats['usd_max']:.4f}")
        print(f"USD/MXN Promedio / Desv : ${stats['usd_avg']:.4f} (± ${stats['usd_stddev']:.4f})")
        print(f"TIIE 28d Mínima / Máxima : {stats['tiie_min']:.2f}% / {stats['tiie_max']:.2f}%")
        print(f"Tasa Real Promedio       : {stats['tasa_real_promedio']:.2f}%")
        print("---")
        print(f"Correlación USD vs TIIE  : {corr['corr_usd_tiie']:+.4f}")
        print(f"Correlación USD vs Inf   : {corr['corr_usd_inflacion']:+.4f}")
        print("========================================================================\n")

    storage.close()


if __name__ == "__main__":
    main()
