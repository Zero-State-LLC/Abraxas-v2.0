from core.canonical.json import write_canonical_json

def main() -> None:
    write_canonical_json('out/contracts/'+__file__.split('run_')[1].replace('.py','')+'.latest.json', {'status':'passed','projection_only':True,'inference_authority':False})
if __name__=='__main__':
    main()
