package com.example.onetry.company.repository;

import com.example.onetry.company.entity.CompanyInfo;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CompanyInfoRepository extends MongoRepository<CompanyInfo, String> {
    // infoNo를 기준으로 특정 회사 정보를 찾는 메서드
    CompanyInfo findByInfoNo(Long infoNo);

    @Query(value = "{}", fields = "{'companyName': 1, '_id': 0}")
    List<String> findAllCompanyNames();
}
